"""中文翻译半透明浮窗。"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QRect, QSettings, QThread, Qt, QObject, Signal, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from app.core.translation_service import TranslationService, TranslationSettings
from app.utils.click_through import set_click_through

from .settings_dialog import SettingsDialog
from .top_bar import TopBar
from .translation_editor import TranslationEditor
from .translation_view import TranslationView


class _TranslationWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, service: TranslationService, text: str, target: str) -> None:
        super().__init__()
        self.service = service
        self.text = text
        self.target = target

    @Slot()
    def run(self) -> None:
        try:
            self.finished.emit(self.service.translate(self.text, self.target))
        except Exception as exc:
            self.failed.emit(str(exc))


class FloatWindow(QWidget):
    """始终置顶、可拖动、可锁定穿透的中文翻译浮窗。"""

    closed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("FloatWindow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.resize(900, 540)
        self.setMinimumSize(300, 360)

        self._locked = False
        self._root_layout = None
        self._lock_overlay = None
        self._translation_thread: QThread | None = None
        self._translation_worker: _TranslationWorker | None = None
        self._pending_source = ""
        self._pending_target = ""
        self._resize_edges = 0
        self._resize_origin = QPoint()
        self._resize_geometry = QRect()
        self._resize_margin = 8
        self._qsettings = QSettings("ScreenDanmaku", "ChineseTranslator")
        self._translation_settings = self._load_settings()

        self._build_ui()
        self._install_resize_filters()
        self.top_bar.settings_clicked.connect(self._open_settings)
        self.top_bar.close_clicked.connect(self.close)
        self.top_bar.lock_toggled.connect(self._on_lock_toggled)
        self.editor.translate_requested.connect(self._translate)

    def _build_ui(self) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self._root_layout = root

        self.top_bar = TopBar(self)
        root.addWidget(self.top_bar)

        content = QWidget(self)
        content.setObjectName("ContentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.translation_view = TranslationView(content)
        content_layout.addWidget(self.translation_view, 1)

        self.editor = TranslationEditor(content)
        self.editor.setFixedHeight(136)
        content_layout.addWidget(self.editor)
        root.addWidget(content, 1)
        outer.addLayout(root)

    def _load_settings(self) -> TranslationSettings:
        defaults = TranslationSettings()
        saved_engine = self._qsettings.value("translation/engine", "")
        if not saved_engine:
            return defaults
        return TranslationSettings(
            engine=str(saved_engine),
            api_url=str(self._qsettings.value("translation/api_url", defaults.api_url)),
            api_key=str(self._qsettings.value("translation/api_key", defaults.api_key)),
            model=str(self._qsettings.value("translation/model", defaults.model)),
            prompt=str(self._qsettings.value("translation/prompt", defaults.prompt)),
        )

    @Slot()
    def _open_settings(self) -> None:
        dialog = SettingsDialog(self._translation_settings, self)
        dialog.settings_saved.connect(self._apply_settings)
        dialog.exec()

    @Slot(object)
    def _apply_settings(self, settings: object) -> None:
        if not isinstance(settings, TranslationSettings):
            return
        self._translation_settings = settings
        self._qsettings.setValue("translation/engine", settings.engine)
        self._qsettings.setValue("translation/api_url", settings.api_url)
        self._qsettings.setValue("translation/api_key", settings.api_key)
        self._qsettings.setValue("translation/model", settings.model)
        self._qsettings.setValue("translation/prompt", settings.prompt)

    @Slot(str)
    def _translate(self, text: str) -> None:
        if self._translation_thread is not None and self._translation_thread.isRunning():
            return

        self._pending_source = text
        self._pending_target = self.translation_view.target_language
        self.editor.set_busy(True)
        self._translation_thread = QThread(self)
        self._translation_worker = _TranslationWorker(
            TranslationService(self._translation_settings),
            text,
            self._pending_target,
        )
        self._translation_worker.moveToThread(self._translation_thread)
        self._translation_thread.started.connect(self._translation_worker.run)
        self._translation_worker.finished.connect(self._translation_finished)
        self._translation_worker.failed.connect(self._translation_failed)
        self._translation_worker.finished.connect(self._translation_thread.quit)
        self._translation_worker.failed.connect(self._translation_thread.quit)
        self._translation_worker.finished.connect(self._translation_worker.deleteLater)
        self._translation_worker.failed.connect(self._translation_worker.deleteLater)
        self._translation_thread.finished.connect(self._translation_thread.deleteLater)
        self._translation_thread.finished.connect(self._translation_thread_finished)
        self._translation_thread.start()

    def _install_resize_filters(self) -> None:
        self.installEventFilter(self)
        for widget in self.findChildren(QWidget):
            widget.setMouseTracking(True)
            widget.installEventFilter(self)

    def eventFilter(self, watched, event) -> bool:
        if self._locked or not isinstance(watched, QWidget):
            return super().eventFilter(watched, event)

        event_type = event.type()
        if event_type in (QEvent.Type.MouseMove, QEvent.Type.MouseButtonPress):
            position = event.globalPosition().toPoint()
            if self._resize_edges:
                if event_type == QEvent.Type.MouseMove:
                    self._apply_resize(position)
                    return True
            else:
                edges = self._resize_edges_at(position)
                watched.setCursor(self._cursor_for_edges(edges))

            if (
                event_type == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                edges = self._resize_edges_at(position)
                if edges:
                    self._resize_edges = edges
                    self._resize_origin = position
                    self._resize_geometry = self.geometry()
                    return True

        elif event_type == QEvent.Type.MouseButtonRelease and self._resize_edges:
            self._resize_edges = 0
            self._resize_geometry = QRect()
            return True
        return super().eventFilter(watched, event)

    def _resize_edges_at(self, position: QPoint) -> int:
        rect = self.frameGeometry()
        margin = self._resize_margin
        edges = 0
        if abs(position.x() - rect.left()) <= margin:
            edges |= 1
        if abs(position.x() - rect.right()) <= margin:
            edges |= 2
        if abs(position.y() - rect.top()) <= margin:
            edges |= 4
        if abs(position.y() - rect.bottom()) <= margin:
            edges |= 8
        return edges

    @staticmethod
    def _cursor_for_edges(edges: int) -> Qt.CursorShape:
        if edges in (1, 2):
            return Qt.CursorShape.SizeHorCursor
        if edges in (4, 8):
            return Qt.CursorShape.SizeVerCursor
        if edges in (1 | 4, 2 | 8):
            return Qt.CursorShape.SizeFDiagCursor
        if edges in (2 | 4, 1 | 8):
            return Qt.CursorShape.SizeBDiagCursor
        return Qt.CursorShape.ArrowCursor

    def _apply_resize(self, position: QPoint) -> None:
        start = self._resize_geometry
        dx = position.x() - self._resize_origin.x()
        dy = position.y() - self._resize_origin.y()
        left, top = start.left(), start.top()
        right, bottom = start.right(), start.bottom()

        if self._resize_edges & 1:
            left = min(start.left() + dx, right - self.minimumWidth() + 1)
        if self._resize_edges & 2:
            right = max(start.right() + dx, left + self.minimumWidth() - 1)
        if self._resize_edges & 4:
            top = min(start.top() + dy, bottom - self.minimumHeight() + 1)
        if self._resize_edges & 8:
            bottom = max(start.bottom() + dy, top + self.minimumHeight() - 1)
        self.setGeometry(QRect(QPoint(left, top), QPoint(right, bottom)))

    @Slot(str)
    def _translation_finished(self, result: str) -> None:
        self.translation_view.append_result(
            self._pending_source,
            self._pending_target,
            result,
        )
        self.editor.set_busy(False)

    @Slot(str)
    def _translation_failed(self, error: str) -> None:
        self.translation_view.append_error(error or "无法连接翻译接口")
        self.editor.set_busy(False)

    @Slot()
    def _translation_thread_finished(self) -> None:
        self._translation_thread = None
        self._translation_worker = None

    @Slot(bool)
    def _on_lock_toggled(self, locked: bool) -> None:
        self._locked = locked
        if locked:
            self._show_lock_overlay()
            set_click_through(self, True)
        else:
            set_click_through(self, False)
            self._hide_lock_overlay()

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        self._sync_lock_overlay()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._sync_lock_overlay()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._lock_overlay is not None:
            self._lock_overlay.close()
        if self._translation_thread is not None and self._translation_thread.isRunning():
            self._translation_thread.quit()
        self.closed.emit()
        super().closeEvent(event)

    def _show_lock_overlay(self) -> None:
        if self._lock_overlay is None:
            self._lock_overlay = QWidget(
                None,
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.Tool,
            )
            self._lock_overlay.setObjectName("LockBarOverlay")
            self._lock_overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            layout = QHBoxLayout(self._lock_overlay)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

        self._root_layout.removeWidget(self.top_bar)
        self.top_bar.set_drag_window(self)
        self.top_bar.setParent(self._lock_overlay)
        self._lock_overlay.layout().addWidget(self.top_bar)
        self.top_bar.show()
        self._sync_lock_overlay()
        self._lock_overlay.show()
        self._lock_overlay.raise_()

    def _hide_lock_overlay(self) -> None:
        if self._lock_overlay is None:
            return
        self._lock_overlay.layout().removeWidget(self.top_bar)
        self.top_bar.setParent(self)
        self._root_layout.insertWidget(0, self.top_bar)
        self.top_bar.set_drag_window(None)
        self.top_bar.show()
        self._lock_overlay.hide()

    def _sync_lock_overlay(self) -> None:
        if self._lock_overlay is None or not self._locked:
            return
        self._lock_overlay.resize(self.width(), self.top_bar.height())
        self._lock_overlay.move(self.frameGeometry().topLeft())
