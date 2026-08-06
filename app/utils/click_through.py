"""锁定/解锁鼠标穿透工具。"""
from __future__ import annotations

import ctypes
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


def set_click_through(widget: QWidget, enabled: bool) -> None:
    """切换 Qt 和 Windows 原生层面的鼠标穿透状态。"""
    widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, enabled)

    if sys.platform != "win32":
        return

    # Qt 的属性只影响 Qt 事件分发；Windows 仍会把整个窗口作为命中区域。
    # WS_EX_TRANSPARENT 让锁定后的主窗口把点击交给下面的应用。
    hwnd = int(widget.winId())
    user32 = ctypes.windll.user32
    get_style = user32.GetWindowLongPtrW
    set_style = user32.SetWindowLongPtrW
    get_style.restype = ctypes.c_longlong
    get_style.argtypes = [ctypes.c_void_p, ctypes.c_int]
    set_style.restype = ctypes.c_longlong
    set_style.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_longlong]

    exstyle_index = -20  # GWL_EXSTYLE
    layered = 0x00080000  # WS_EX_LAYERED
    transparent = 0x00000020  # WS_EX_TRANSPARENT
    exstyle = int(get_style(hwnd, exstyle_index))
    if enabled:
        exstyle |= layered | transparent
    else:
        exstyle &= ~transparent
    set_style(hwnd, exstyle_index, exstyle)

    # Apply the changed extended style immediately.
    user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0027)
