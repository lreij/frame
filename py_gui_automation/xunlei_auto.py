# -*- coding:gb2312 -*-
"""
将h.lst中的mp3地址，自动加入到迅雷
---------------------------------------------------------------------
eg: h.lst
---------------------------------------------------------------------
http://file3.top100.cn/201105142251/170B3032764E02FCBA5EA6A013FF4C89/Special_129518/Bach,%20JS%20%20%20St%20John%20Passion%20BWV245%20%20%20Part%202%20Es%20ist%20vollbracht%20%5BContralto%5D.mp3
http://file3.top100.cn/201105142251/A6DA2419CA6671FD10495008BA558523/Special_129518/Bach,%20JS%20%20%20St%20John%20Passion%20BWV245%20%20%20Part%202%20Da%20sprach%20Pilatus%20zu%20ihm...%20Barrabas%20aber%20war%20ein%20Morder%20%5BEvangelist,%20Pilate,%20Jesus,%20Chorus%5D.mp3
http://file3.top100.cn/201105142251/49F6B462E0C9713B25DF8F4F33EAE4D9/Special_129518/Bach,%20JS%20%20%20St%20John%20Passion%20BWV245%20%20%20Part%201%20Ach,%20mein%20Sinn%20%5BTenor%5D.mp3
http://file3.top100.cn/201105142251/F28CD29C11459696140097B5D10FA540/Special_129518/Bach,%20JS%20%20%20St%20John%20Passion%20BWV245%20%20%20Part%201%20Dein%20Will%20gescheh,%20Herr%20Gott,%20zugleich%20%5BChorus%5D.mp3
---------------------------------------------------------------------

note:
---------------------------------------------------------------------
def ActivateWindow(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
---------------------------------------------------------------------
.pyw 脚本后台运行
---------------------------------------------------------------------
"""

from watsup.winGuiAuto import findTopWindow
from SendKeys import SendKeys
from time import sleep
import win32clipboard
import win32con
import win32gui

def ActivateWindow(hwnd):
    #win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
    #make the window topmost!
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST,
            0, 0, 0, 0, win32con.SWP_SHOWWINDOW)

def setText(aString):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_TEXT, aString)
    win32clipboard.CloseClipboard()

def run():
    for addr in open('h.lst'): 
        setText(addr) 
        xl = findTopWindow(wantedText='迅雷5')
        ActivateWindow(xl)
        SendKeys('^n')
        sleep(1)
        SendKeys('{ENTER}')

def test():
    xl = findTopWindow(wantedText='迅雷5')
    ActivateWindow(xl)

if __name__ == '__main__':
    run()
