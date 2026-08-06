"""中文输入区。"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class TranslationEditor(QWidget):
    """下方中文输入和翻译操作区。"""

    translate_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("TranslationEditor")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 12)
        layout.setSpacing(6)

        header = QHBoxLayout()
        header.addWidget(QLabel("中文输入", self))
        header.addStretch(1)
        self.status_label = QLabel("", self)
        self.status_label.setObjectName("EditorStatus")
        header.addWidget(self.status_label)
        layout.addLayout(header)

        row = QHBoxLayout()
        row.setSpacing(10)
        self.input = QPlainTextEdit(self)
        self.input.setObjectName("TranslationInput")
        self.input.setPlaceholderText("输入中文，按 Ctrl+Enter 翻译")
        self.input.setFixedHeight(62)
        self.input.installEventFilter(self)
        row.addWidget(self.input, 1)

        self.translate_button = QPushButton("翻译", self)
        self.translate_button.setObjectName("TranslateBtn")
        self.translate_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.translate_button.setFixedWidth(76)
        self.translate_button.clicked.connect(self._request_translation)
        row.addWidget(self.translate_button, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addLayout(row)

    def eventFilter(self, obj, event) -> bool:
        if obj is self.input and event.type() == event.Type.KeyPress:
            if (
                event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                and event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                self._request_translation()
                return True
        return super().eventFilter(obj, event)

    def _request_translation(self) -> None:
        text = self.input.toPlainText().strip()
        if text:
            self.translate_requested.emit(text)

    def set_busy(self, busy: bool) -> None:
        self.translate_button.setEnabled(not busy)
        self.input.setEnabled(not busy)
        self.status_label.setText("翻译中..." if busy else "")

    def clear_input(self) -> None:
        self.input.clear()

    def focus_input(self) -> None:
        self.input.setFocus()
