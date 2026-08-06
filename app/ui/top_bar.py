"""翻译浮窗顶部控制栏。"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class TopBar(QWidget):
    """设置、标题、关闭和锁定控制。"""

    settings_clicked = Signal()
    close_clicked = Signal()
    lock_toggled = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("TopBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(46)
        self._drag_pos = None
        self._drag_window = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        self.btn_settings = QPushButton("⚙", self)
        self.btn_settings.setObjectName("IconBtn")
        self.btn_settings.setToolTip("翻译设置")

        self.btn_close = QPushButton("✕", self)
        self.btn_close.setObjectName("IconBtn")
        self.btn_close.setToolTip("关闭浮窗")

        self.btn_lock = QPushButton("🔓", self)
        self.btn_lock.setObjectName("IconBtn")
        self.btn_lock.setProperty("name", "lock")
        self.btn_lock.setProperty("locked", "false")
        self.btn_lock.setCheckable(True)
        self.btn_lock.setToolTip("锁定 / 解锁")

        layout.addStretch(1)
        layout.addWidget(self.btn_settings)
        layout.addWidget(self.btn_close)
        layout.addWidget(self.btn_lock)

        self.btn_settings.clicked.connect(self.settings_clicked.emit)
        self.btn_close.clicked.connect(self.close_clicked.emit)
        self.btn_lock.toggled.connect(self._on_lock_toggled)

    def _on_lock_toggled(self, checked: bool) -> None:
        self.btn_lock.setProperty("locked", "true" if checked else "false")
        self.btn_lock.setText("🔒" if checked else "🔓")
        self.btn_lock.style().unpolish(self.btn_lock)
        self.btn_lock.style().polish(self.btn_lock)
        self.lock_toggled.emit(checked)

    def set_drag_window(self, window: QWidget | None) -> None:
        self._drag_window = window

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            window = self._drag_window or self.window()
            if window is not None:
                self._drag_pos = event.globalPosition().toPoint() - window.pos()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            window = self._drag_window or self.window()
            if window is not None:
                window.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None
        event.accept()
