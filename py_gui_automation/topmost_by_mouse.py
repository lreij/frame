# -*- coding:utf-8 -*-
## Jerry Lu <lreij@163.com>
""""""
import win32gui, win32con
raw_input("mouse on window, press Enter")
point = win32gui.GetCursorPos()
hwnd = win32gui.WindowFromPoint(point)
while win32gui.GetParent(hwnd) != 0:
    hwnd = win32gui.GetParent(hwnd)
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
