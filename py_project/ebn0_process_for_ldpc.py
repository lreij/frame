# -*- coding: utf-8 -*-
import os
import re
import shutil
import win32com
from win32com.client import Dispatch

FIRST_ROW = 0
LAST_ROW = 0
RESULT_FOLDER = r'results'
TEMPLATE = r'template\ebn0.xls'
OUTPUT_FILE = os.path.join(os.getcwd(), 'ebn0.xls')
shutil.copyfile(TEMPLATE, OUTPUT_FILE)
excel = win32com.client.Dispatch("Excel.Application");
excel.Visible = 0
excel.DisplayAlerts = 0
ebn0 = excel.Workbooks.Open(OUTPUT_FILE)
s = ebn0.Worksheets

def group_results():
    d = {}
    def to_dict(filename):
        p_ff_phy = re.compile('QAM.*_phy\d')
        m = p_ff_phy.search(filename)
        ff_phy = m.group().replace('_LDPC_E_MMU3A_test', '')
        if ff_phy not in d: d[ff_phy] = []
        d[ff_phy].append(os.path.join(RESULT_FOLDER, filename))
    map(to_dict, os.listdir(RESULT_FOLDER))
    return d

def add_sheet(sheet_name):
    s("Sheet1").Copy(Before=s("Sheet1"))
    ebn0.ActiveSheet.Name = sheet_name

def update_chart(sheet_name):
    c = s(sheet_name).ChartObjects(1).Chart
    c.ChartTitle.Text = "Ebn0_%s_LDPC" % sheet_name
    c.Axes()[0].MinimumScale = \
            float(s(sheet_name).Range("A%i" % FIRST_ROW).Value) - 0.3
    c.Axes()[0].MaximumScale = \
            float(s(sheet_name).Range("A%i" % LAST_ROW).Value) + 0.3

def add_curve(sheet_name, raw_data, i):
    p_p = re.compile('P[MN](\d{1,2})')
    m = p_p.search(raw_data)
    if 'M' in m.group(): 
        pm = 1
        anchor = "P%i" % (int(m.group(1))+1)
    else: 
        pm = 0
        anchor = "O%i" % (int(m.group(1))+1)
    r_num = int(m.group(1))*20 + 30 + pm*16*20
    raw = excel.Workbooks.Open(os.path.abspath(raw_data))
    rows_count = int(raw.Sheets(1).UsedRange.Rows.Count)
    global FIRST_ROW, LAST_ROW
    FIRST_ROW = r_num
    LAST_ROW = r_num+rows_count-3
    raw.Sheets(1).Range("A3:Y%i" % rows_count).Copy()
    s(sheet_name).Range("A%i:Y%i" % (r_num, LAST_ROW)).PasteSpecial()
    raw.Close()
    s(sheet_name).Range(anchor).Value = m.group()
    s(sheet_name).Hyperlinks.Add(Anchor=s(sheet_name).Range(anchor),
            Address="", SubAddress="A%i" % (r_num-1))
    s(sheet_name).Range("A%i" % (r_num-1)).Value = m.group()
    s(sheet_name).Range("B%i" % (r_num-1)).Value = "Top"
    s(sheet_name).Hyperlinks.Add(Anchor=s(sheet_name).Range("B%i" %(r_num-1)),
            Address="", SubAddress="N1")
    c = s(sheet_name).ChartObjects(1).Chart
    c.SeriesCollection().NewSeries()
    c.SeriesCollection()[i+1].Name = m.group()
    c.SeriesCollection()[i+1].XValues = \
            s(sheet_name).Range("A%i:A%i" % (r_num, LAST_ROW))
    c.SeriesCollection()[i+1].Values = \
            s(sheet_name).Range("B%i:B%i" % (r_num, LAST_ROW))

def process_ff_per_phy(ff_per_phy):
    add_sheet(ff_per_phy[0])
    ff_per_phy[1].sort()
    def ac_(n):
        add_curve(ff_per_phy[0], ff_per_phy[1][n], n)
    map(ac_, range(len(ff_per_phy[1])))
    update_chart(ff_per_phy[0])

def close_excel():
    ebn0.Worksheets("Sheet1").Delete()
    ebn0.Save()
    ebn0.Close()

def generate():
    results = group_results()
    map(process_ff_per_phy, results.items())
    close_excel()
    
if __name__ == '__main__':
    try: generate()
    finally: excel.Quit()
