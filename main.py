"""中文翻译浮窗程序入口。"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.ui.float_window import FloatWindow
from app.ui.style import GLOBAL_QSS


def _resource_path(relative_path: str) -> Path:
    bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return bundle_root / relative_path


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("中文翻译浮窗")
    icon = QIcon(str(_resource_path("msg/bird.jpg")))
    app.setWindowIcon(icon)
    app.setStyleSheet(GLOBAL_QSS)

    window = FloatWindow()
    window.setWindowIcon(icon)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
