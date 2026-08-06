"""中文翻译浮窗程序入口。"""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.ui.float_window import FloatWindow
from app.ui.style import GLOBAL_QSS


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("中文翻译浮窗")
    app.setStyleSheet(GLOBAL_QSS)

    window = FloatWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
