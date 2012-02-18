# -*- coding:utf-8 -*-
import os
import win32com
from win32com.client import Dispatch


def full_name(name):
    return os.path.join(os.getcwd(), name)


e = win32com.client.Dispatch("Excel.application")
e.Visible = 0
e.DisplayAlerts = 0
report = e.Workbooks.Open(full_name('a.xls'))
sheets = report.WorkSheets


s = sheets("Spectrum_QAM4")
c = s.ChartObjects(3).Chart
c.Export(full_name('a.jpg'))
c.Export(full_name('a.png'))
c.Export(full_name('a.gif'))


report.Close()
e.Quit()

