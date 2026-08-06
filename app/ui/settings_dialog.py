"""翻译引擎设置窗口。"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
)

from app.core.translation_service import ENGINE_DEFAULT_URLS, TranslationSettings


class SettingsDialog(QDialog):
    """编辑翻译引擎、地址、模型和提示词。"""

    settings_saved = Signal(object)

    def __init__(self, settings: TranslationSettings, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SettingsDialog")
        self.setWindowTitle("翻译设置")
        self.setModal(True)
        self.setMinimumWidth(540)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(10)

        hint = QLabel("常规引擎无需 API Key；AI 大模型需要可用的 OpenAI 兼容接口。", self)
        hint.setObjectName("SettingsHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(9)

        self.engine_combo = QComboBox(self)
        self.engine_combo.addItems(
            ["Google", "MyMemory（免费）", "LibreTranslate", "AI 大模型"]
        )
        self.engine_combo.setCurrentText(settings.engine)
        self._last_engine = settings.engine
        self.engine_combo.currentTextChanged.connect(self._engine_changed)
        form.addRow("翻译引擎", self.engine_combo)

        self.url_edit = QLineEdit(settings.api_url, self)
        form.addRow("API 地址", self.url_edit)

        self.key_edit = QLineEdit(settings.api_key, self)
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_edit.setPlaceholderText("免费引擎可留空")
        form.addRow("API Key", self.key_edit)

        self.model_edit = QLineEdit(settings.model, self)
        self.model_edit.setPlaceholderText("例如 qwen2.5:7b")
        form.addRow("模型", self.model_edit)
        layout.addLayout(form)

        prompt_label = QLabel("提示词（仅 AI 大模型使用，支持 {from} / {to}）", self)
        prompt_label.setObjectName("SettingsHint")
        layout.addWidget(prompt_label)
        self.prompt_edit = QPlainTextEdit(self)
        self.prompt_edit.setObjectName("PromptEdit")
        self.prompt_edit.setPlainText(settings.prompt)
        self.prompt_edit.setFixedHeight(78)
        layout.addWidget(self.prompt_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("保存")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._engine_changed(self.engine_combo.currentText())

    def _engine_changed(self, engine: str) -> None:
        if engine != self._last_engine and engine in ENGINE_DEFAULT_URLS:
            self.url_edit.setText(ENGINE_DEFAULT_URLS[engine])
        self._last_engine = engine
        is_ai = engine == "AI 大模型"
        needs_key = engine in {"AI 大模型", "LibreTranslate"}
        self.key_edit.setEnabled(needs_key)
        self.model_edit.setEnabled(is_ai)
        self.prompt_edit.setEnabled(is_ai)

    def _save(self) -> None:
        engine = self.engine_combo.currentText()
        settings = TranslationSettings(
            engine=engine,
            api_url=self.url_edit.text().strip(),
            api_key=self.key_edit.text(),
            model=self.model_edit.text().strip(),
            prompt=self.prompt_edit.toPlainText().strip(),
        )
        if not settings.api_url or (engine == "AI 大模型" and not settings.model):
            return
        self.settings_saved.emit(settings)
        self.accept()
