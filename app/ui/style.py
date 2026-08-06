"""中文翻译浮窗 QSS。"""

GLOBAL_QSS = """
* {
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
    color: rgba(32, 33, 36, 214);
}

#FloatWindow {
    background: rgba(220, 224, 228, 0.70);
    border: 1px solid rgba(40, 45, 50, 0.32);
    border-radius: 14px;
}

#TopBar {
    background: rgba(245, 247, 249, 0.74);
    border-bottom: 1px solid rgba(50, 55, 60, 0.20);
    border-top-left-radius: 14px;
    border-top-right-radius: 14px;
}

QPushButton#IconBtn {
    min-width: 30px;
    max-width: 30px;
    min-height: 30px;
    max-height: 30px;
    border: none;
    border-radius: 15px;
    background: rgba(40, 45, 50, 0.10);
    color: rgba(60, 65, 69, 220);
    font-size: 15px;
}
QPushButton#IconBtn:hover { background: rgba(40, 45, 50, 0.20); }
QPushButton#IconBtn[name="lock"][locked="true"] {
    background: #e26d4f;
    color: white;
}

#ContentArea { background: transparent; }

#TranslationView {
    background: rgba(248, 249, 250, 0.58);
    border: 2px solid rgba(35, 136, 220, 0.78);
    border-radius: 14px;
}

#TranslationOutput {
    background: transparent;
    border: none;
    padding: 4px 2px;
    selection-background-color: rgba(35, 136, 220, 0.24);
}

#TranslationView QLabel {
    color: rgba(99, 104, 108, 210);
    font-size: 12px;
}

QComboBox#TargetLanguage {
    min-width: 110px;
    min-height: 30px;
    padding: 2px 10px;
    border: 1px solid rgba(40, 45, 50, 0.28);
    border-radius: 7px;
    background: rgba(255, 255, 255, 0.74);
}
QComboBox#TargetLanguage:hover { border-color: #2388dc; }
QComboBox#TargetLanguage QAbstractItemView {
    background: #f8f9fa;
    border: 1px solid rgba(40, 45, 50, 0.22);
    selection-background-color: rgba(35, 136, 220, 0.20);
}

#TranslationEditor {
    background: rgba(248, 249, 250, 0.62);
    border: 2px solid rgba(50, 166, 76, 0.76);
    border-radius: 14px;
}

#TranslationEditor QLabel { color: #4b8058; font-weight: 600; }
#TranslationEditor QLabel#EditorStatus { color: #777d80; font-weight: 400; }

#TranslationInput {
    background: rgba(255, 255, 255, 0.50);
    border: 1px solid rgba(40, 45, 50, 0.20);
    border-radius: 7px;
    padding: 6px 8px;
}
#TranslationInput:focus { border-color: rgba(35, 136, 220, 0.70); }

QPushButton#TranslateBtn {
    min-height: 36px;
    border: none;
    border-radius: 7px;
    background: #2388dc;
    color: white;
    font-weight: 600;
}
QPushButton#TranslateBtn:hover { background: #1975c0; }
QPushButton#TranslateBtn:disabled { background: rgba(35, 136, 220, 0.42); }

#SettingsDialog {
    background: rgba(245, 247, 249, 0.98);
}
#SettingsHint { color: #687075; }
#SettingsDialog QLineEdit {
    min-height: 30px;
    padding: 2px 7px;
    border: 1px solid rgba(40, 45, 50, 0.22);
    border-radius: 6px;
    background: white;
}
#SettingsDialog QComboBox,
#SettingsDialog QPlainTextEdit {
    min-height: 30px;
    padding: 2px 7px;
    border: 1px solid rgba(40, 45, 50, 0.22);
    border-radius: 6px;
    background: white;
}
#SettingsDialog QPlainTextEdit { padding: 6px 7px; }
#SettingsDialog QDialogButtonBox QPushButton {
    min-width: 76px;
    min-height: 30px;
    border: none;
    border-radius: 6px;
    background: #2388dc;
    color: white;
}
"""
