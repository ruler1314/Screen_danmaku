"""翻译结果显示区。"""
from __future__ import annotations

import time

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class TranslationView(QFrame):
    """上方翻译查看区，固定为只读输出。"""

    target_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("TranslationView")
        self._history: list[tuple[str, str, str]] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 10)
        layout.setSpacing(8)

        self.output = QPlainTextEdit(self)
        self.output.setObjectName("TranslationOutput")
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("翻译结果会显示在这里")
        self.output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.output, 1)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.addStretch(1)
        footer.addWidget(QLabel("翻译成", self))
        self.target_combo = QComboBox(self)
        self.target_combo.setObjectName("TargetLanguage")
        self.target_combo.addItems(
            [
                "英语",
                "日语",
                "韩语",
                "法语",
                "德语",
                "西班牙语",
                "俄语",
                "意大利语",
            ]
        )
        self.target_combo.currentTextChanged.connect(self.target_changed.emit)
        footer.addWidget(self.target_combo)
        layout.addLayout(footer)

    @property
    def target_language(self) -> str:
        return self.target_combo.currentText()

    @property
    def history(self) -> list[tuple[str, str, str]]:
        """本次程序运行中的历史，不写入磁盘。"""
        return list(self._history)

    def append_result(self, source: str, target: str, result: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self._history.append((source, target, result))
        if self.output.toPlainText():
            self.output.appendPlainText("")
        self.output.appendPlainText(
            f"{timestamp}  翻译成{target}\n"
            f"原文：{source.strip()}\n"
            f"译文：{result.strip()}"
        )
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())

    def append_error(self, text: str) -> None:
        if self.output.toPlainText():
            self.output.appendPlainText("")
        self.output.appendPlainText(f"翻译失败：{text}")
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())
