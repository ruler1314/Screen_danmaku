"""中文翻译浮窗程序入口。"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from app.ui.float_window import FloatWindow
from app.ui.style import GLOBAL_QSS


def _resource_path(relative_path: str) -> Path:
    bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return bundle_root / relative_path


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("中文翻译浮窗")
    app.setQuitOnLastWindowClosed(True)
    icon = QIcon(str(_resource_path("msg/bird.jpg")))
    app.setWindowIcon(icon)
    app.setStyleSheet(GLOBAL_QSS)

    window = FloatWindow()
    window.setWindowIcon(icon)

    tray = None
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray = QSystemTrayIcon(icon, app)
        tray.setToolTip("中文翻译浮窗")

        tray_menu = QMenu()
        restore_action = QAction("打开翻译窗口", tray_menu)
        quit_action = QAction("退出程序", tray_menu)
        tray_menu.addAction(restore_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        tray.setContextMenu(tray_menu)

        def restore_window() -> None:
            window.showNormal()
            window.raise_()
            window.activateWindow()

        restore_action.triggered.connect(restore_window)
        quit_action.triggered.connect(window.close)
        tray.activated.connect(
            lambda reason: restore_window()
            if reason
            in (
                QSystemTrayIcon.ActivationReason.Trigger,
                QSystemTrayIcon.ActivationReason.DoubleClick,
            )
            else None
        )
        app.aboutToQuit.connect(tray.hide)
        tray.show()

    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
