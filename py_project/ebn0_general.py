# -*- coding: utf-8 -*-
# ELURUIJ
from Tkinter import *
import tkFileDialog, tkFont
import os
import re
import shutil
import ConfigParser
import win32com
from win32com.client import Dispatch

EBN0 = 0
RBER = 0
MSE = 0
INDEX = 2
CURVE_NAME = ''
EBN0_TEMPLATE = r'template\Eb_N0.xls'
RBER_TEMPLATE = r'template\R_BER.xls'
EBN0_MSE_TEMPLATE = r'template\Eb_N0_MSE.xls'
RS = r'template\rs.ini'
EBN0_OUTPUT_FILE = r'output\Eb_N0.xls'
RBER_OUTPUT_FILE = r'output\R_BER.xls'
e = None
ebn0 = None
rber = None
s = None

def excel_init():
    global e
    e = win32com.client.Dispatch("Excel.Application");
    e.Visible = 0
    e.DisplayAlerts = 0

def excel_close():
    global e
    e.Quit()

def excel_wrapper(func):
    def wrapper_it(*args, **argv):
        excel_init()
        try: func(*args, **argv)
        except Exception, error:
            print error
        finally: excel_close()
    return wrapper_it 

def rs(ff):
    _rs = (0, 0)
    c = ConfigParser.ConfigParser()
    c.read(RS)
    try:
        _rs = (c.get(ff, 'E-3'), c.get(ff, 'E-6'))
    except ConfigParser.NoSectionError:
        print '\nNo RS\n'
        _rs = (0, 0)
    return _rs

def get_sheet_name(filename):
    ff_name_p = re.compile(r'(QAM|CQPSK).*?(_[AE]|E1)_')
    phy_name_p = re.compile(r'phy\d')
    m1 = ff_name_p.search(filename)
    m2 = phy_name_p.search(filename)
    if "AD" in m1.group():
        s_name = m1.group() + m2.group()
    else:
        s_name = m1.group()[:-1]
    if len(s_name) > 30:
        s_name = s_name.replace('ADAPTIVE', 'AD')
    return s_name

def generate_ebn0(filename):
    print 'ebn0\t', filename
    global e, INDEX, ebn0, s, MSE
    sheet_name = get_sheet_name(filename)
    s("Sheet1").Copy(Before=s("Sheet1"))
    ebn0.ActiveSheet.Name = sheet_name
    raw = e.Workbooks.Open(filename)
    rows_count = int(raw.Sheets(1).UsedRange.Rows.Count)
    last_ebn0 = raw.Sheets(1).Range("B%i" % rows_count).Value
    if str(last_ebn0) == "       NaN" or str(last_ebn0) == "0.0":
        rows_count = rows_count - 1
    raw.Sheets(1).Range("A3:Y%i" % rows_count).Copy()
    s(sheet_name).Range("A3:Y%i" % rows_count).PasteSpecial()
    raw.Close()
    s(sheet_name).Range("O38").Value = rs(sheet_name)[0]
    s(sheet_name).Range("O39").Value = rs(sheet_name)[1]
    c = s(sheet_name).ChartObjects(1).Chart
    c.ChartTitle.Text = "Ebn0_%s" % sheet_name
    c.Axes()[0].MinimumScale = float(s(sheet_name).Range("A3").Value) - 0.2
    c.Axes()[0].MaximumScale = float(s(sheet_name).Range("A%s" % (rows_count)).Value) + 0.2
    if MSE:
        c2 = s(sheet_name).ChartObjects(2).Chart
        c2.ChartTitle.Text = "MSE/BER_%s" % sheet_name
        c2.Axes()[0].MaximumScale = float(s(sheet_name).Range("B3").Value) * 10
        c2.Axes()[0].MinimumScale = float(s(sheet_name).Range("B%s" % (rows_count)).Value) / 10
        c2.Axes()[1].MinimumScale = float(s(sheet_name).Range("Y3").Value) - 0.5
        c2.Axes()[1].MaximumScale = float(s(sheet_name).Range("Y%s" % (rows_count)).Value) + 0.5
        c2.Axes()[1].MajorUnit = (c2.Axes()[1].MaximumScale - c2.Axes()[1].MinimumScale) / 5
    s("summary").Range("A%i" % INDEX).Value = sheet_name
    s("summary").Hyperlinks.Add(Anchor=s("summary").Range("A%i" % INDEX),
            Address="", SubAddress="%s!A1" % (sheet_name))
    s(sheet_name).Hyperlinks.Add(Anchor=s(sheet_name).Range("N37"),
            Address="", SubAddress="summary!A%i" % (INDEX))
    INDEX = INDEX + 1
    ebn0.Save()
    print "\t\tDone"
    
def generate_rber(filename):
    print 'rber\t', filename
    global e, INDEX, rber, s
    sheet_name = get_sheet_name(filename)
    s("Sheet1").Copy(Before=s("Sheet1"))
    rber.ActiveSheet.Name = sheet_name
    raw = e.Workbooks.Open(filename)
    rows_count = int(raw.Sheets(1).UsedRange.Rows.Count)
    last_ebn0 = raw.Sheets(1).Range("B%i" % rows_count).Value
    if str(last_ebn0) == "       NaN" or str(last_ebn0) == "0.0":
        rows_count = rows_count - 1
    raw.Sheets(1).Range("A3:B%s" % (rows_count)).Copy()
    s(sheet_name).Range("A3:B%s" % (rows_count)).PasteSpecial()
    raw.Sheets(1).Range("C3:Y%s" % (rows_count)).Copy()
    s(sheet_name).Range("D3:Z%s" % (rows_count)).PasteSpecial()
    raw.Close()
    s(sheet_name).Range("A%s" % (rows_count+1)).Value = s(sheet_name).Range("A%s" % (rows_count)).Value + 0.5
    s(sheet_name).Range("A%s" % (rows_count+2)).Value = s(sheet_name).Range("A%s" % (rows_count)).Value + 1
    s(sheet_name).Range("A%s" % (rows_count+3)).Value = s(sheet_name).Range("A%s" % (rows_count)).Value + 1.5  
    s(sheet_name).Range("C%s" % (rows_count)).Value = "=(LOG(B%s)-LOG(B%s))/(A%s-A%s)" % \
    (rows_count, rows_count-1, rows_count, rows_count-1) 
    s(sheet_name).Range("C%s" % (rows_count+1)).Value = s(sheet_name).Range("C%s" % (rows_count)).Value
    s(sheet_name).Range("C%s" % (rows_count+2)).Value = s(sheet_name).Range("C%s" % (rows_count)).Value
    s(sheet_name).Range("C%s" % (rows_count+3)).Value = s(sheet_name).Range("C%s" % (rows_count)).Value
    s(sheet_name).Range("B%s" % (rows_count+1)).Value = "=10^(C%s*(A%s-A%s)+LOG(B%s))" % \
    (rows_count+1, rows_count+1, rows_count, rows_count)
    s(sheet_name).Range("B%s" % (rows_count+2)).Value = "=10^(C%s*(A%s-A%s)+LOG(B%s))" % \
    (rows_count+2, rows_count+2, rows_count+1, rows_count+1)
    s(sheet_name).Range("B%s" % (rows_count+3)).Value = "=10^(C%s*(A%s-A%s)+LOG(B%s))" % \
    (rows_count+3, rows_count+3, rows_count+2, rows_count+2)
    c = s(sheet_name).ChartObjects(1).Chart
    c.ChartTitle.Text = "RBER_%s" % sheet_name
    c.Axes()[0].MinimumScale = float(s(sheet_name).Range("A3").Value) - 0.2
    c.Axes()[0].MaximumScale = float(s(sheet_name).Range("A%s" % (rows_count)).Value) + 1.7
    rber.Save()
    print "\tDone"

@excel_wrapper
def generate_ebn0_and_rber(filenames):
    shutil.copyfile(RBER_TEMPLATE, RBER_OUTPUT_FILE)
    global e, ebn0, rber, s, INDEX, MSE
    if MSE:
        shutil.copyfile(EBN0_MSE_TEMPLATE, EBN0_OUTPUT_FILE)
    else:
        shutil.copyfile(EBN0_TEMPLATE, EBN0_OUTPUT_FILE)
    if EBN0: 
        ebn0 = e.Workbooks.Open(os.path.join(os.getcwd(), EBN0_OUTPUT_FILE))
        s = ebn0.Worksheets
        map(generate_ebn0, filenames)
        s("Sheet1").Delete()
        ebn0.Save()
        ebn0.Close()
    else: 
        os.remove(EBN0_OUTPUT_FILE)
    if RBER: 
        rber = e.Workbooks.Open(os.path.join(os.getcwd(), RBER_OUTPUT_FILE))
        s = rber.Worksheets
        map(generate_rber, filenames)
        s("Sheet1").Delete()
        rber.Save()
        rber.Close()
    else: 
        os.remove(RBER_OUTPUT_FILE)
    INDEX = 2
    print '\n\n\nFinish!'

def add_ebn0(filename):
    print 'add ebn0', filename
    global e, INDEX, ebn0, s, CURVE_NAME
    sheet_name = get_sheet_name(filename)
    all_sheets = map(lambda x: s(x+1).Name, range(s.Count))
    if sheet_name in all_sheets:
        c = s(sheet_name).ChartObjects(1).Chart
        i_new_curve = c.SeriesCollection().Count - 5
        i_new_data = 50 + i_new_curve * 30
        raw = e.Workbooks.Open(filename)
        rows_count = int(raw.Sheets(1).UsedRange.Rows.Count)
        last_ebn0 = raw.Sheets(1).Range("B%i" % rows_count).Value
        if str(last_ebn0) == "       NaN" or str(last_ebn0) == "0.0":
            rows_count = rows_count - 1
        raw.Sheets(1).Range("A3:Y%i" % rows_count).Copy()
        s(sheet_name).Range("A%i:Y%i" % (i_new_data, i_new_data+rows_count-3)).PasteSpecial()
        raw.Close()
        c.SeriesCollection().NewSeries()
        c.SeriesCollection()[i_new_curve+5].Name = CURVE_NAME
        c.SeriesCollection()[i_new_curve+5].XValues = \
            s(sheet_name).Range("A%i:A%i" % (i_new_data, i_new_data+rows_count-3))
        c.SeriesCollection()[i_new_curve+5].Values = \
            s(sheet_name).Range("B%i:B%i" % (i_new_data, i_new_data+rows_count-3))
        ebn0.Save()
    else:
        print "FF not found, can't plot the comparing curve!"
    print '\tDone'

@excel_wrapper
def compare_ebn0(filenames):
    global e, ebn0, s, CURVE_NAME
    if os.path.exists(os.path.join(os.getcwd(), EBN0_OUTPUT_FILE)):
        ebn0 = e.Workbooks.Open(os.path.join(os.getcwd(), EBN0_OUTPUT_FILE))
        s = ebn0.Worksheets
        map(add_ebn0, filenames)
        ebn0.Save()
        ebn0.Close()
    print '\n\n\nFinish!'

class App(Frame):
    def select_data(self):
        return tkFileDialog.askopenfilenames(
                filetypes=[('excel files', '.xls'),],
                initialdir='.',
                title='Please select ebn0...')

    def generate(self):
        global EBN0, RBER, MSE
        EBN0 = self.is_g_ebn0_var.get()
        RBER = self.is_g_rber_var.get()
        MSE = self.is_g_mse_var.get()
        if MSE == 1: EBN0 = 1
        generate_ebn0_and_rber(self.select_data())

    def compare(self):
        global CURVE_NAME
        CURVE_NAME = self.new_curve_name.get()
        compare_ebn0(self.select_data())

    def createWidgets(self):
        font = tkFont.Font(family="consolas", size=18)
        self.is_g_ebn0_var = IntVar()
        self.is_g_ebn0 = Checkbutton(self, text="Ebn0", font=font,
                variable=self.is_g_ebn0_var, onvalue=1, offvalue=0)
        self.is_g_ebn0.grid(row=0, column=0, padx=10, pady=20)
        self.is_g_ebn0_var.set(1)
        self.is_g_rber_var = IntVar()
        self.is_g_rber = Checkbutton(self, text="RBER", font=font,
                variable=self.is_g_rber_var, onvalue=1, offvalue=0)
        self.is_g_rber.grid(row=0, column=1, padx=10, pady=20)
        self.is_g_mse_var = IntVar()
        self.is_g_mse = Checkbutton(self, text="MSE", font=font,
                variable=self.is_g_mse_var, onvalue=1, offvalue=0)
        self.is_g_mse.grid(row=0, column=2, padx=10, pady=20)
        self.is_g_mse_var.set(1)
        self.generate_ebn0 = Button(self, fg="blue", text="Generate", 
                command=self.generate, height=2, width=16, font=font)
        self.generate_ebn0.grid(row=0, column=3, padx=10, pady=20)
        Label(self, text="Curve Name:", 
                font=font).grid(row=1, column=0, padx=10)
        self.new_curve_name = Entry(self, font=font, width=10)
        self.new_curve_name.grid(row=1, column=1, padx=10)
        self.compare_ebn0 = Button(self, fg="blue", text="Compare", 
                command=self.compare, height=2, width=16, font=font)
        self.compare_ebn0.grid(row=1, column=3, padx=10, pady=20)
        self.QUIT = Button(self, text="QUIT", fg="red", 
                command=self.quit, height=2, width=16, font=font)
        self.QUIT.grid(row=2, column=3, padx=10, pady=20)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

if __name__ == '__main__':
    root = Tk()
    root.title("ebn0/rber plot")
    app = App(master=root)
    app.mainloop()
    root.destroy()
