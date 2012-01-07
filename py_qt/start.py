# -*- coding:utf-8 -*-
## lreij
from __future__ import with_statement
import os
import sys
sys.path.append(r'.\libs')
from ConfigParser import ConfigParser
import MySQLdb
import datetime
import time
import shutil
import parse
import re
import traceback
import win32com
from win32com.client import Dispatch, constants
from PyQt4 import QtCore, QtGui
from mainui import Ui_MainWindow
from result_update import Ui_result_update_dlg
from dut_information import Ui_dut_information_dlg

# production env
host = "150.236.56.87"
user = "root"
passwd = "root"
database = "ff"
"""
# test env
host = "localhost"
user = "root"
passwd = ""
database = "fff"
"""

# TODO: Hop, Alignment
# globals
"""
case_seq = ["Spectrum_Sprious"]
"""
case_seq = ["MSE", "PhyModeSwitch", "Number of E1DS1",
    "Delay", "Equipment Delay", "DCN", "RFLockIn",
    "RPS", "Signature", "Jitter", "Jitter on Tx sample PWM",
    "CIR", "EbN0", "Spectrum_Sprious", "Power", "Hop", "Alignment Delay"]
case_mapper = {"MSE": "MSE", "RPS": "RPS", "DCN": "DCN",
    "Signature": "Signature", "Number of E1DS1": "Num_of_E1", 
    "RFLockIn": "RFLockIn", "PhyModeSwitch": "PhyModeSwitch",
    "Delay": "Delay", "Equipment Delay": "Equipment_Delay",
    "Jitter": "Jitter", "Jitter on Tx sample PWM": "Jitter_PWM",
    "CIR": "CIR", "EbN0": "Ebn0", "Spectrum_Sprious": "Spectrum_Spurious",
    "Hop": "Hop", "Alignment Delay": "Alignment_Delay", "Power": "Power"}
index = 0
e = None
sheets = None
report = None
report_file = ""
phymodes = []
modulations = []
summary_index = 4
ff_mode = ""
base_path = ""
platform = ""
frame_format = ""
dut_infor = ""
generation_warning = ""
mid_dict = {}
records = []

def excel_init():
    global e, report, sheets
    e = win32com.client.Dispatch("Excel.Application")
    e.Visible = 0
    e.DisplayAlerts = 0
    report = e.Workbooks.Open(report_file)
    sheets = report.WorkSheets

def excel_open():
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = 1 
    excel.Workbooks.Open(report_file)

def excel_close():
    global report, e
    report.Save()
    report.Close()
    e.Quit()

def get_cs(ff):
    if 'CS' in ff:
        p = re.compile("CS(\d*)")
        m = p.search(ff)
        if m:
            return m.group(1)
    else:
        p = re.compile("(\d*)xE1")
        m = p.search(ff)
        if m:
            d = {"22": "14", "46": "28", "35": "14", "75": "28"}
            return d[m.group(1)]

def get_rs(ff, modulation, testcase):
    global base_path
    rs_path = os.path.join(base_path, r"configuration\RS.ini")
    sec_path = os.path.join(base_path, r"configuration\sec.ini")
    spectrum_mask_path = os.path.join(base_path, 
        r"configuration\spectrum_mask.ini")
    if testcase == "Spectrum_Spurious":
        c = ConfigParser()
        c.read(sec_path)
        try:
            sec = c.get("sec", ff)
            c1 = ConfigParser()
            c1.read(spectrum_mask_path)
            cs = get_cs(ff)
            mask = c1.get(sec, cs)
            return mask.split(",")
        except:
            return None
    else:
        c = ConfigParser()
        c.read(rs_path)
        try:
            v = c.get(ff, modulation)
            l = v.split(",")
            if testcase == "Equipment_Delay":
                return [l[0], l[1]]
            elif testcase == "Ebn0":
                return [l[3], l[4]]
            elif testcase == "Signature":
                return [l[5], l[6]]
        except:
            return None

def get_testcase_result(result):
    return result.split('\n')[-1].strip()

def logger(log):
    print log
    f = open(os.path.join(base_path, r"template\logfile.txt"), "a")
    t = datetime.datetime.now().strftime("%Y/%m/%d %H:%M    ")
    f.write(str(t) + str(log) + "\n")
    f.close()

def clear_logfile_if_big_than_500k():
    logfile = os.path.join(base_path, r"template\logfile.txt")
    if os.stat(logfile).st_size / 1024 > 500:
        f = open(logfile, 'w')
        f.close()

def debug_information(func):
    def wrapper(self):
        logger(type(self))
        logger(self.result[1])
        try:
            func(self)
        except Exception, e:
            global generation_warning
            gen_err_str = "Testcase: %s, Modulation: %s, Error: %s\n\n" % \
                (self.result[0], self.result[1], e)
            generation_warning += gen_err_str
            logger("\n" + traceback.format_exc())
    return wrapper

class base_handler(object):
    def __init__(self, result):
        self.result = result

    def go(self):
        pass

class MSE(base_handler):
    def __copy_cell(self):
        self.phy = get_phy_from_modulation(self.result[1])
        self.s = sheets("MSE")
        self.s.Range("A100:C100").Copy()
        row = modulations.index(self.result[1].strip()) + 6
        self.s.Range("A%i:C%i" % (row, row)).PasteSpecial()

    def __insert_value_to_cell(self):
        row = modulations.index(self.result[1].strip()) + 6
        self.s.Range("A%i" % row).Value = self.phy
        self.s.Range("B%i" % row).Value = self.result[1]
        self.s.Range("C%i" % row).Value = self.result[2].split("\r\n")[0]

    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = \
            self.result[0].strip()
        sheets("Summary").Range("B%i" % summary_index).Value = \
            self.result[1].strip()
        sheets("Summary").Range("C%i" % summary_index).Value = "Pass"
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="MSE!A1")
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        self.__copy_cell()
        self.__insert_value_to_cell()
        self.__update_summary()

class Ebn0(base_handler):
    def __get_sheet_name(self):
        if ff_mode is "LEGACY":
            self.s = sheets("EbN0")
            self.t = sheets("RBER")
        else:
            self.r = sheets("All_Phymodes_EbN0")
            sheets("EbN0").Copy(Before=sheets("EbN0"))
            name = "EbN0_QAM" + self.result[1].strip()
            report.ActiveSheet.Name = name
            self.s = sheets(name)
            sheets("RBER").Copy(Before=sheets("RBER"))
            name = "RBER_QAM" + self.result[1].strip()
            report.ActiveSheet.Name = name
            self.t = sheets(name)

    def __ebn0_result(self):
        ebn0_temp = os.path.join(base_path, 'template', 'ebn0_temp.xls')
        with open(ebn0_temp, 'w') as f:
            f.write(self.result[2])
        raw = e.Workbooks.Open(ebn0_temp)
        self.rows_count = int(raw.Sheets(1).UsedRange.Rows.Count) - 3
        last_ebn0 = raw.Sheets(1).Range("B%i" % self.rows_count).Value
        while str(last_ebn0) == "       NaN" or str(last_ebn0) == "0.0":
            self.rows_count = self.rows_count - 1
            last_ebn0 = raw.Sheets(1).Range("B%i" % self.rows_count).Value
        raw.Sheets(1).Range("A1:Y%i" % self.rows_count).Copy()
        self.s.Range("A40:Y%i" % (40+self.rows_count)).PasteSpecial()
        raw.Close()
        os.remove(ebn0_temp)
        self.s.Range("A5").Value = "QAM" + self.result[1].strip()
        rs = get_rs(frame_format, self.result[1].strip(), "Ebn0")
        if rs is not None:
            self.s.Range("B35").Value = rs[0]
            self.s.Range("B36").Value = rs[1]
        c1 = self.s.ChartObjects(7).Chart
        c1.Axes()[0].MinimumScale = float(self.s.Range("A42").Value) - 0.2
        c1.Axes()[0].MaximumScale = \
            float(self.s.Range("A%i" % (39+self.rows_count)).Value) + 0.2
        c2 = self.s.ChartObjects(8).Chart
        c2.Axes()[0].MaximumScale = float(self.s.Range("B42").Value) * 10
        c2.Axes()[0].MinimumScale = \
            float(self.s.Range("B%i" % (39+self.rows_count)).Value) / 10
        c2.Axes()[1].MinimumScale = float(self.s.Range("Y42").Value) - 0.5
        c2.Axes()[1].MaximumScale = \
            float(self.s.Range("Y%i" % (39+self.rows_count)).Value) + 0.5
        c2.Axes()[1].MajorUnit = \
            (c2.Axes()[1].MaximumScale - c2.Axes()[1].MinimumScale) / 5
        
    def __rber_result(self):
        rows_count = self.rows_count + 39
        self.s.Range("A42:B%s" % (rows_count)).Copy()
        self.t.Range("A42:B%s" % (rows_count)).PasteSpecial()
        self.s.Range("C42:Y%s" % (rows_count)).Copy()
        self.t.Range("D42:Z%s" % (rows_count)).PasteSpecial()
        self.t.Range("A%s" % (rows_count+1)).Value = \
            self.t.Range("A%s" % (rows_count)).Value + 0.5
        self.t.Range("A%s" % (rows_count+2)).Value = \
            self.t.Range("A%s" % (rows_count)).Value + 1
        self.t.Range("A%s" % (rows_count+3)).Value = \
            self.t.Range("A%s" % (rows_count)).Value + 1.5  
        self.t.Range("C%s" % (rows_count)).Value = \
            "=(LOG(B%s)-LOG(B%s))/(A%s-A%s)" % \
            (rows_count, rows_count-1, rows_count, rows_count-1) 
        self.t.Range("C%s" % (rows_count+1)).Value = \
            self.t.Range("C%s" % (rows_count)).Value
        self.t.Range("C%s" % (rows_count+2)).Value = \
            self.t.Range("C%s" % (rows_count)).Value
        self.t.Range("C%s" % (rows_count+3)).Value = \
            self.t.Range("C%s" % (rows_count)).Value
        self.t.Range("B%s" % (rows_count+1)).Value = \
            "=10^(C%s*(A%s-A%s)+LOG(B%s))" % \
            (rows_count+1, rows_count+1, rows_count, rows_count)
        self.t.Range("B%s" % (rows_count+2)).Value = \
            "=10^(C%s*(A%s-A%s)+LOG(B%s))" % \
            (rows_count+2, rows_count+2, rows_count+1, rows_count+1)
        self.t.Range("B%s" % (rows_count+3)).Value = \
            "=10^(C%s*(A%s-A%s)+LOG(B%s))" % \
            (rows_count+3, rows_count+3, rows_count+2, rows_count+2)
        self.t.Range("A5").Value = "QAM" + self.result[1].strip()
        self.t.Range("B35").Value = ""
        c = self.t.ChartObjects(4).Chart
        c.Axes()[0].MinimumScale = float(self.t.Range("A42").Value) - 0.2
        c.Axes()[0].MaximumScale = \
            float(self.t.Range("A%s" % (rows_count)).Value) + 1.7

    def __all_ebn0_cureve(self):
        if ff_mode is "ADAPTIVE":
            c = self.r.ChartObjects(1).Chart
            i_curve = c.SeriesCollection().Count
            c.SeriesCollection().NewSeries()
            c.SeriesCollection()[i_curve].Name = self.s.Name
            c.SeriesCollection()[i_curve].XValues = \
                self.s.Range("A%i:A%i" % (42, 39 + self.rows_count))
            c.SeriesCollection()[i_curve].Values = \
                self.s.Range("B%i:B%i" % (42, 39 + self.rows_count))


    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = "EbN0"
        sheets("Summary").Range("B%i" % summary_index).Value = \
            self.result[1].strip()
        sheets("Summary").Range("C%i" % summary_index).Value = "Done"
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="%s!A1" % self.s.Name)
        sheets("Summary").Range("A%i" % (summary_index + 1)).Value = "RBER"
        sheets("Summary").Range("B%i" % (summary_index + 1)).Value = \
            self.result[1].strip()
        sheets("Summary").Range("C%i" % (summary_index + 1)).Value = "Done"
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % (summary_index + 1)),
            Address="", SubAddress="%s!A1" % self.t.Name)
        summary_index = summary_index + 2

    @debug_information
    def go(self):
        self.__get_sheet_name()
        self.__ebn0_result()
        self.__rber_result()
        self.__all_ebn0_cureve()
        self.__update_summary()

class RPS(base_handler):
    def __common(self):
        self.phy = get_phy_from_modulation(self.result[1])
        self.s = sheets("RPS")
        self.row = modulations.index(self.result[1].strip()) * 2 + 7

    def __noise_go(self):
        p = parse.compile('''HBER_WARNING activation level:\n\
\tNoise = {}, BERT = {}, Bit[6] = {};\n\
HBER_WARNING de-activation level:\n\
\tNoise = {}, BERT = {}, Bit[6] = {};\n\
HBER_WARNING hysteretic level:\n\
\t[{}, {}]\n\
LBER_WARNING activation level:\n\
\tNoise = {}, BERT = {}, Bit[7] = {};\n\
LBER_WARNING de-activation level:\n\
\tNoise = {}, BERT = {}, Bit[7] = {};\n\
LBER_WARNING hysteretic level:\n\
\t[{}, {}]\n\
EBER_WARNING activation level:\n\
\tNoise = {}, BERT = {}, Bit[10] = {};\n\
EBER_WARNING de-activation level:\n\
\tNoise = {}, BERT = {}, Bit[10] = {};\n\
EBER_WARNING hysteretic level:\n\
\t[{}, {}]\r\n\
{}''')
        cells = p.parse(self.result[2].strip())

        self.s.Range("A100:L101").Copy()
        self.s.Range("A5:L6").PasteSpecial()
        row = self.phy + 7
        self.s.Range("A102:L103").Copy()
        self.s.Range("A%i:L%i" % (self.row, self.row+1)).PasteSpecial()

        self.s.Range("A%i" % self.row).Value = self.phy
        self.s.Range("B%i" % self.row).Value = self.result[1]

        def insert_cells(i, c, row):
            self.s.Range("%s%i" % (c, row)).Value = cells[i]
            self.s.Range("%s%i" % (chr(ord(c)+1), row)).Value = cells[i+1]
            self.s.Range("%s%i" % (chr(ord(c)+2), row)).Value = cells[i+2]

        insert_cells(0, 'D', self.row)
        insert_cells(3, 'D', self.row+1)
        insert_cells(8, 'G', self.row)
        insert_cells(11, 'G', self.row+1)
        insert_cells(16, 'J', self.row)
        insert_cells(19, 'J', self.row+1)

        self.pass_or_fail = cells[24]

    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = \
            self.result[0].strip()
        sheets("Summary").Range("B%i" % summary_index).Value = \
            self.result[1].strip()
        sheets("Summary").Range("C%i" % summary_index).Value = \
            self.pass_or_fail
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="RPS!A1")
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        self.__common()
        if "Noise" in self.result[2]:
            self.__noise_go()
        self.__update_summary()

class DCN(base_handler):
    def __copy_cell(self):
        self.phy = get_phy_from_modulation(self.result[1])
        self.s = sheets("DCN")
        self.s.Range("A100:D100").Copy()
        row = modulations.index(self.result[1].strip()) + 6
        self.s.Range("A%i:D%i" % (row, row)).PasteSpecial()

    def __insert_value_to_cell(self):
        p = re.compile(r"(\d*.\d*) KHz")
        m = p.findall(self.result[2].strip())
        if m:
            cells = m
        else:
            cells = [0,0,0]
        row = modulations.index(self.result[1].strip()) + 6
        self.s.Range("A%i" % row).Value = self.phy
        self.s.Range("B%i" % row).Value = self.result[1]
        self.s.Range("C%i" % row).Value = cells[1]
        self.s.Range("D%i" % row).Value = cells[2]
        p1 = re.compile(r"(Pass|Fail)")
        m = p1.search(self.result[2].strip())
        if m:
            self.pass_or_fail = m.group()
        else:
            self.pass_or_fail = "Fail"

    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = \
            self.result[0].strip()
        sheets("Summary").Range("B%i" % summary_index).Value = \
            self.result[1].strip()
        sheets("Summary").Range("C%i" % summary_index).Value = \
            self.pass_or_fail
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="DCN!A1")
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        self.__copy_cell()
        self.__insert_value_to_cell()
        self.__update_summary()

class Signature(base_handler):
    def __copy_cell(self):
        self.phy = get_phy_from_modulation(self.result[1])
        row = modulations.index(self.result[1].strip()) * 12 + 6
        self.s = sheets("Signature")
        self.s.Range("A200:F211").Copy()
        self.s.Range("A%i:F%i" % (
            row, row+11)).PasteSpecial()

    def __insert_value_to_cell(self):
        temp = os.path.join(base_path, 'template', 'temp.xls')
        with open(temp, 'w') as f:
            f.write(self.result[2].replace('\r', ''))
        raw = e.Workbooks.Open(temp)
        raw.Sheets(1).Range("A2:D13").Copy()
        row = modulations.index(self.result[1].strip()) * 12 + 6
        self.s.Range("C%i:F%i" % (
            row, 11+row)).PasteSpecial(Paste=-4163)
        self.pass_or_fail = raw.Sheets(1).Range("A15").Value
        raw.Close()
        os.remove(temp)
        self.s.Range("A%i" % (row)).Value = self.phy
        self.s.Range("B%i" % (row)).Value = self.result[1]

    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = \
            self.result[0].strip()
        sheets("Summary").Range("B%i" % summary_index).Value = \
            self.result[1].strip()
        sheets("Summary").Range("C%i" % summary_index).Value = \
            self.pass_or_fail
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="Signature!A1")
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        self.__copy_cell()
        self.__insert_value_to_cell()
        self.__update_summary()

class Num_of_E1(base_handler):
    def __copy_cell(self):
        self.phy = get_phy_from_modulation(self.result[1])
        self.s = sheets("Number_of_E1DS1")
        self.s.Range("A100:E100").Copy()
        row = modulations.index(self.result[1].strip()) + 7 
        self.s.Range("A%i:E%i" % (row, row)).PasteSpecial()

    def __insert_value_to_cell(self):
        row = modulations.index(self.result[1].strip()) + 7 
        p = re.compile(r"is (.*)")
        m = p.search(self.result[2].strip())
        if m:
            self.s.Range("C%i" % row).Value = m.group(1)
        p1 = re.compile(r"traffic (.*)")
        m1 = p1.findall(self.result[2].strip())
        if m1:
            self.s.Range("D%i" % row).Value = m1[0]
            self.s.Range("E%i" % row).Value = m1[1].replace('.', '')
        self.s.Range("A%i" % row).Value = self.phy
        self.s.Range("B%i" % row).Value = self.result[1]
        p2 = re.compile(r"(Pass|Fail)")
        m2 = p2.search(self.result[2].strip())
        if m:
            self.pass_or_fail = m2.group()
        else:
            self.pass_or_fail = "Fail"

    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = \
            self.result[0].strip()
        sheets("Summary").Range("B%i" % summary_index).Value = \
            self.result[1].strip()
        sheets("Summary").Range("C%i" % summary_index).Value = \
            self.pass_or_fail
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="Number_of_E1DS1!A1")
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        self.__copy_cell()
        self.__insert_value_to_cell()
        self.__update_summary()

class RFLockIn(base_handler):
    def __copy_cell(self):
        self.phy = get_phy_from_modulation(self.result[1])
        self.s = sheets("RF_lock_in")
        self.s.Range("A100:E100").Copy()
        row = modulations.index(self.result[1].strip()) + 7
        self.s.Range("A%i:E%i" % (row, row)).PasteSpecial()

    def __insert_value_to_cell(self):
        row = modulations.index(self.result[1].strip()) + 7
        self.s.Range("A%i" % row).Value = self.phy
        self.s.Range("B%i" % row).Value = self.result[1]
        p = re.compile(r"(\d*.\d*)ms")
        m = p.findall(self.result[2].strip())
        if m:
            self.s.Range("C%i" % row).Value = m[0]
            self.s.Range("D%i" % row).Value = m[1]
            self.s.Range("E%i" % row).Value = m[2]
        p2 = re.compile(r"(Pass|Fail)")
        m2 = p2.search(self.result[2].strip())
        if m:
            self.pass_or_fail = m2.group()
        else:
            self.pass_or_fail = "Fail"
    
    # TODO
    def __insert_curves(self):
        pass

    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = \
            self.result[0].strip()
        sheets("Summary").Range("B%i" % summary_index).Value = \
            self.result[1].strip()
        sheets("Summary").Range("C%i" % summary_index).Value = \
            self.pass_or_fail
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="RF_lock_in!A1")
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        self.__copy_cell()
        self.__insert_value_to_cell()
        self.__update_summary()

class PhyModeSwitch(base_handler):
    def __copy_cell(self):
        self.phy = get_phy_from_modulation(self.result[1])
        self.s = sheets("Phymodes_switch")

    def __insert_value_to_cell(self):
        p = re.compile(r"=(.*),Phymode=(\d)")
        m = p.findall(self.result[2])
        if m:
            for i in xrange(len(m)-1):
                if m[i][1] != m[i+1][1]:
                    row = i + 8
                    self.s.Range("A100:D100").Copy()
                    self.s.Range("A%i:D%i" % (row, row)).PasteSpecial()
                    self.s.Range("A%i" % row).Value = "%s > %s" % \
                        (m[i][1], m[i+1][1])
                    self.s.Range("C%i" % row).Value = "%s > %s" % \
                        (get_modulation_from_phy(m[i][1]),
                        get_modulation_from_phy(m[i+1][1]))
                    self.s.Range("D%i" % row).Value = m[i+1][0]
        self.pass_or_fail = get_testcase_result(self.result[2].strip())
    
    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = \
            self.result[0].strip()
        sheets("Summary").Range("C%i" % summary_index).Value = \
            self.pass_or_fail
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="Phymodes_switch!A1")
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        if self.result[1].strip() == '4':
            self.__copy_cell()
            self.__insert_value_to_cell()
            self.__update_summary()

class Delay(base_handler):
    def __copy_cell(self):
        self.phy = get_phy_from_modulation(self.result[1])
        self.s = sheets("Delay")

    def __insert_value_to_cell(self):
        p = re.compile(r"(\d)\t(.*)\t(.*)\t(.*)")
        m = p.findall(self.result[2])
        if m:
            for i in xrange(len(m)):
                row = i + 7
                self.s.Range("A100:E100").Copy()
                self.s.Range("A%i:E%i" % (row, row)).PasteSpecial()
                self.s.Range("A%i" % row).Value = m[i][0]
                self.s.Range("B%i" % row).Value = \
                    get_modulation_from_phy(m[i][0])
                self.s.Range("C%i" % row).Value = m[i][1]
                self.s.Range("D%i" % row).Value = m[i][2]
                self.s.Range("E%i" % row).Value = m[i][3]
        self.pass_or_fail = get_testcase_result(self.result[2].strip())
    
    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = \
            self.result[0].strip()
        sheets("Summary").Range("C%i" % summary_index).Value = \
            self.pass_or_fail
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="Delay!A1")
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        if self.result[1].strip() == '4':
            self.__copy_cell()
            self.__insert_value_to_cell()
            self.__update_summary()

class Equipment_Delay(base_handler):
    def __copy_cell(self):
        self.phy = get_phy_from_modulation(self.result[1])
        self.s = sheets("Equipment_Delay")

    def __insert_value_to_cell(self):
        p = re.compile(r"(\d)\t(.*)")
        m = p.findall(self.result[2])
        if m:
            for i in xrange(len(m)):
                row = i + 6 
                self.s.Range("A100:C100").Copy()
                self.s.Range("A%i:C%i" % (row, row)).PasteSpecial()
                self.s.Range("A%i" % row).Value = m[i][0]
                self.s.Range("B%i" % row).Value = \
                    get_modulation_from_phy(m[i][0])
                self.s.Range("C%i" % row).Value = m[i][1]
        p1 = re.compile(r"is (.*)")
        m1 = p1.findall(self.result[2])
        if m1:
            self.s.Range("A21").Value = m1[0]
    
    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = \
            self.result[0].strip()
        sheets("Summary").Range("C%i" % summary_index).Value = \
            self.pass_or_fail
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="Equipment_Delay!A1")
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        if self.result[1].strip() == '4':
            self.__copy_cell()
            self.__insert_value_to_cell()
            self.__update_summary()

class Jitter(base_handler):
    def __insert_picture(self):
        self.s = sheets("Jitter_Wander")
        self.s.Pictures().Insert(self.result[2])
        os.remove(self.result[2])

    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = \
            self.result[0].strip()
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="Jitter_Wander!A1")
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        self.__insert_picture()
        self.__update_summary()

class Jitter_PWM(base_handler):
    def __insert_picture(self):
        self.s = sheets("Jitter_PWM")
        self.s.Pictures().Insert(self.result[2])
        os.remove(self.result[2])

    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = \
            self.result[0].strip()
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="Jitter_PWM!A1")
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        self.__insert_picture()
        self.__update_summary()

class CIR(base_handler):
    def __get_sheet_name(self):
        if ff_mode is "LEGACY":
            self.s = sheets("CIR")
        else:
            sheets("CIR").Copy(Before=sheets("CIR"))
            name = "CIR_QAM" + self.result[1].strip()
            report.ActiveSheet.Name = name
            self.s = sheets(name)

    def __cir_result(self):
        temp = os.path.join(base_path, 'template', 'temp.xls')
        with open(temp, 'w') as f:
            f.write(self.result[2])
        raw = e.Workbooks.Open(temp)
        self.rows_count = int(raw.Sheets(1).UsedRange.Rows.Count)
        raw.Sheets(1).Range("A1:G%i" % self.rows_count).Copy()
        self.s.Range("A40:G%i" % (self.rows_count+39)).PasteSpecial()
        raw.Close()
        os.remove(temp)
        self.s.Range("A5").Value = "QAM" + self.result[1].strip()
        c = self.s.ChartObjects(1).Chart
        c.Axes()[0].MinimumScale = float(self.s.Range("A42").Value) - 5 
        c.Axes()[0].MaximumScale = \
            float(self.s.Range("A%i" % (39+self.rows_count)).Value) + 5

    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = "CIR"
        sheets("Summary").Range("B%i" % summary_index).Value = \
            self.result[1].strip()
        sheets("Summary").Range("C%i" % summary_index).Value = "Done"
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="%s!A1" % self.s.Name)
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        self.__get_sheet_name()
        self.__cir_result()
        self.__update_summary()

class Power(base_handler):
    def __insert_value_to_cell(self):
        if ff_mode is "LEGACY":
            self.s = sheets("Spectrum")
        else:
            name = "Spectrum_QAM" + self.result[1].strip()
            self.s = sheets(name)
        def get_value(s):
            p = re.compile(r"is (.*) dBm")
            m = p.search(s)
            if m:
                return m.group(1)
            return 0
        self.s.Range("B8").Value = get_value(self.result[2])

    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = \
            self.result[0].strip()
        sheets("Summary").Range("B%i" % summary_index).Value = \
            self.result[1].strip()
        if -2 < float(self.s.Range("B8").Value) < 2:
            sheets("Summary").Range("C%i" % summary_index).Value = "Pass"
        else:
            sheets("Summary").Range("C%i" % summary_index).Value = "Fail"
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="%s!A1" % self.s.Name)
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        self.__insert_value_to_cell()
        self.__update_summary()

class Spectrum_Spurious(base_handler):
    def __init_result(self):
        self.result[2] = mid_dict[self.result[0] + self.result[1]]

    def __check_market(self):
        self.m = "E"
        p = re.compile(r"_A$")
        m = p.search(frame_format)
        if m:
            self.m = "A"

    def __get_sheet_name(self):
        def copy_sheet(sheet_name):
            if ff_mode is "LEGACY":
                self.s = sheets(sheet_name)
                self.s.Name = "Spectrum"
            else:
                sheets(sheet_name).Copy(Before=sheets(sheet_name))
                name = "Spectrum_QAM" + self.result[1].strip()
                report.ActiveSheet.Name = name
                self.s = sheets(name)
        if self.m is "A":
            copy_sheet("Spectrum_A")
        else:
            copy_sheet("Spectrum_E")
        self.s.Range("A5").Value = "QAM" + self.result[1].strip()

    def __result_E(self):
        temp = os.path.join(base_path, 'template', 'temp.xls')
        with open(temp, 'w') as f:
            f.write(self.result[2].replace('\r', ''))
        raw = e.Workbooks.Open(temp)
        raw.Sheets(1).Range("A9:B8009").Copy()
        self.s.Range("A18:B8018").PasteSpecial()
        raw.Sheets(1).Range("A8013:B16013").Copy()
        self.s.Range("C18:D8018").PasteSpecial()
        self.s.Range("B7").Value = raw.Sheets(1).Range("A16016").Value
        def get_value(s):
            p = re.compile(r":(.*)")
            m = p.search(str(s))
            if m:
                return m.group(1)
            return 0
        self.s.Range("B12").Value = get_cs(frame_format)
        self.s.Range("C12").Value = get_value(raw.Sheets(1).Range("A9").Value)
        self.s.Range("D12").Value = get_value(raw.Sheets(1).Range("A5").Value)
        self.s.Range("E12").Value = get_value(raw.Sheets(1).Range("A5").Value)
        raw.Close()
        os.remove(temp)
        if "CQPSK" in frame_format:
            self.s.Range("AA109:AA131").Copy()
        else:
            self.s.Range("AB109:AB131").Copy()
        self.s.Range("R109:R131").PasteSpecial()
        kf = get_rs(frame_format, self.result[1].strip(), "Spectrum_Spurious")
        if kf is not None:
            k = [x for x in kf if kf.index(x) % 2 == 0]
            f = [x for x in kf if kf.index(x) % 2 != 0]
            def __t(l, x):
                l.insert(0, 350 - float(x))
                l.append(350 + float(x))
            l = []
            map(lambda x: __t(l, x), f)
            cs = get_cs(frame_format)
            l.insert(0, 350 - 2.5 * float(cs))
            l.append(350 + 2.5 * float(cs))
            l.insert(len(l)/2, 350)
            def __s(l, x):
                l.insert(0, x)
                l.append(x)
            n = []
            map(lambda x: __s(n, x), k)
            n.insert(0, k[-1])
            n.append(k[-1])
            n.insert(len(n)/2, k[0])
            def _insert_value(column, l):
                def __insert(column, l, x):
                    self.s.Range("%s%i" % (column, 139+x)).Value = l[x],
                map(lambda x: __insert(column, l, x), xrange(len(l)))
            _insert_value('Q', kf)
            _insert_value('R', l)
            _insert_value('S', n)
    
    def __result_A(self):
        temp = os.path.join(base_path, 'template', 'temp.xls')
        with open(temp, 'w') as f:
            f.write(self.result[2].replace('\r', ''))
        raw = e.Workbooks.Open(temp)
        raw.Sheets(1).Range("A9:B8009").Copy()
        self.s.Range("AM15:AN8015").PasteSpecial()
        raw.Sheets(1).Range("A8013:A16013").Copy()
        self.s.Range("AO16:AO8016").PasteSpecial()
        raw.Sheets(1).Range("B8013:B16013").Copy()
        self.s.Range("Y16:Y8016").PasteSpecial()
        self.s.Range("B7").Value = raw.Sheets(1).Range("A16016").Value
        def get_value(s):
            p = re.compile(r":(.*)")
            m = p.search(str(s))
            if m:
                return m.group(1)
            return 0
        self.s.Range("AN9").Value = get_cs(frame_format)
        self.s.Range("AO9").Value = get_value(raw.Sheets(1).Range("A6").Value)
        self.s.Range("AP9").Value = get_value(raw.Sheets(1).Range("A2").Value)
        self.s.Range("AQ9").Value = get_value(raw.Sheets(1).Range("A4").Value)
        self.s.Range("C6").Value = self.s.Range("AN9").Value
        self.s.Range("C8").Value = self.s.Range("AP9").Value
        raw.Close()
        os.remove(temp)
        if "CQPSK" in frame_format:
            self.s.Range("E109:E131").Copy()
        else:
            self.s.Range("F109:F131").Copy()
        self.s.Range("B109:B131").PasteSpecial()

    def __result(self):
        if self.m is "A":
            self.__result_A()
        else:
            self.__result_E()

    def __update_summary(self):
        global summary_index
        sheets("Summary").Range("A%i" % summary_index).Value = "Spectrum"
        sheets("Summary").Range("B%i" % summary_index).Value = \
            self.result[1].strip()
        sheets("Summary").Range("C%i" % summary_index).Value = "Done"
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="%s!A1" % self.s.Name)
        summary_index = summary_index + 1
        sheets("Summary").Range("A%i" % summary_index).Value = "Spurious"
        sheets("Summary").Range("B%i" % summary_index).Value = \
            self.result[1].strip()
        sheets("Summary").Range("C%i" % summary_index).Value = "Done"
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="%s!A1" % self.s.Name)
        summary_index = summary_index + 1
        sheets("Summary").Range("A%i" % summary_index).Value = "TX C/N"
        sheets("Summary").Range("B%i" % summary_index).Value = \
            self.result[1].strip()
        if float(self.s.Range("B7").Value) > 63:
            sheets("Summary").Range("C%i" % summary_index).Value = "Pass"
        else:
            sheets("Summary").Range("C%i" % summary_index).Value = "Fail"
        sheets("summary").Hyperlinks.Add(
            Anchor=sheets("summary").Range("A%i" % summary_index),
            Address="", SubAddress="%s!A1" % self.s.Name)
        summary_index = summary_index + 1

    @debug_information
    def go(self):
        self.__init_result()
        self.__check_market()
        self.__get_sheet_name()
        self.__result()
        self.__update_summary()

def get_platform_prefix():
    c = ConfigParser()
    c.read(os.path.join(base_path, r"configuration\Platform.ini"))
    return c.get(platform, 'prefix')

def get_product_number(for_doc_name):
    c = ConfigParser()
    c.read(os.path.join(base_path, r"configuration\FrameFormat.ini"))
    v = c.get(frame_format, 'product_number')
    if for_doc_name:
        return v.replace(" ", "").replace("/", "_")
    else:
        return v

def get_phymodes():
    global phymodes
    c = ConfigParser()
    c.read(os.path.join(base_path, r"configuration\FrameFormat.ini"))
    v = c.get(frame_format, 'phymodes')
    phymodes = v.split(",")


def get_modulations():
    global modulations 
    c = ConfigParser()
    c.read(os.path.join(base_path, r"configuration\FrameFormat.ini"))
    v = c.get(frame_format, 'modulations')
    modulations = v.split(",")

def get_phy_from_modulation(m):
    return int(phymodes[modulations.index(m)])

def get_modulation_from_phy(p):
    return modulations[phymodes.index(p)]

def get_report_file_name():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S ") + \
        "10265-" + \
        get_platform_prefix() + "_" + \
        get_product_number(True) + ".xls"

def get_ff_mode():
    global ff_mode
    if 'AD' in frame_format:
        ff_mode = "ADAPTIVE"
    else:
        ff_mode = "LEGACY"

def copy_template():
    global report_file
    report_file = os.path.join(base_path, 'report', get_report_file_name())
    shutil.copyfile(os.path.join(
        base_path, r'template\VR_template.xls'), report_file)

def add_all_ebn0_sheet_to_summary():
    global summary_index
    sheets("Summary").Range("A%i" % summary_index).Value = "All_Phymodes_EbN0"
    sheets("Summary").Range("B%i" % summary_index).Value = ""
    sheets("Summary").Range("C%i" % summary_index).Value = ""
    sheets("summary").Hyperlinks.Add(
        Anchor=sheets("summary").Range("A%i" % summary_index),
        Address="", SubAddress="All_Phymodes_EbN0!A1")
    summary_index = summary_index + 1

def add_other_sheets_to_summary():
    global summary_index
    sheets("Summary").Range("A%i" % summary_index).Value = "Hop"
    sheets("Summary").Range("B%i" % summary_index).Value = ""
    sheets("Summary").Range("C%i" % summary_index).Value = ""
    sheets("summary").Hyperlinks.Add(
        Anchor=sheets("summary").Range("A%i" % summary_index),
        Address="", SubAddress="Hop!A1")
    summary_index = summary_index + 1
    sheets("Summary").Range("A%i" % summary_index).Value = "Alignment_Delay"
    sheets("Summary").Range("B%i" % summary_index).Value = ""
    sheets("Summary").Range("C%i" % summary_index).Value = ""
    sheets("summary").Hyperlinks.Add(
        Anchor=sheets("summary").Range("A%i" % summary_index),
        Address="", SubAddress="Alignment_Delay!A1")
    summary_index = summary_index + 1

def update_dut_information():
    def get_infor(pattern, i):
        p = re.compile(pattern)
        m = p.search(dut_infor)
        if m:
            return m.group(i)
        return ""
    s = sheets("VR")
    s.Range("D2").Value = "Verification Report For " + frame_format
    s.Range("D7").Value = "10265-" + \
        get_platform_prefix() + "/" + \
        get_product_number(False)
    s.Range("G7").Value = "PA1"
    s.Range("E10").Value = get_infor(r"DUT: (.*)", 1)
    s.Range("F10").Value = "N/A"
    s.Range("G10").Value = "N/A"
    s.Range("F11").Value = get_infor(r"(CXP9.*?_\d)(\w\d+\w\d+)", 1)
    s.Range("G11").Value = get_infor(r"(CXP9.*?_\d)(\w\d+\w\d+)", 2)
    s.Range("F12").Value = get_infor(r"(CXC17.*_\d)(.*)", 1)
    s.Range("G12").Value = get_infor(r"(CXC17.*_\d)(.*)", 2)
    s.Range("E15").Value = get_infor(r"on: (.*)", 1)
    s.Range("D21").Value = "1056-" + get_product_number(False)
    s.Range("E21").Value = "N/A"
    s.Range("D25").Value = "PA1"
    s.Range("E25").Value = datetime.datetime.now().strftime("%Y-%m-%d")
    s.Range("F25").Value = "N/A"
    s.Range("G25").Value = "N/A"

def setup():
    get_ff_mode()
    get_phymodes()
    get_modulations()
    copy_template()
    excel_init()

def teardown():
    update_dut_information()
    if ff_mode is "ADAPTIVE":
        sheets("Spectrum_E").Delete()
        sheets("Spectrum_A").Delete()
        sheets("EbN0").Delete()
        sheets("RBER").Delete()
        sheets("CIR").Delete()
        sheets("Jitter_Wander").Delete()
        sheets("Jitter_PWM").Delete()
        add_all_ebn0_sheet_to_summary()
    else:
        sheets("All_Phymodes_EbN0").Delete()
        sheets("Phymodes_switch").Delete()

def generate():
    setup()
    map(lambda x: getattr(x, 'go')(), 
        map(lambda x,y: globals()[case_mapper[x.strip()]](y), 
            map(lambda x: x[0], 
                records), records))
    teardown()

def table_exist(table):
    exist = True
    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=database)
    sql = """describe %s;""" % table
    c = db.cursor()
    try:
        c.execute(sql)
    except Exception, e:
        exist = False
    finally:
        c.close()
        db.close()
        return exist

def get_records_from_db(table, testcase, modulation):
    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=database)
    sql = """select testcase, qam, result, time from %s
where testcase='%s' and qam='%s' order by id desc;""" \
    % (table, testcase, modulation)
    c = db.cursor()
    try:
        c.execute(sql)
        records = list(c.fetchone())
        if records[0] in ["Jitter", "Jitter on Tx sample PWM"]:
            file_name = base_path + '\\template\\' + \
                datetime.datetime.now().strftime("%y%m%d%H%M%S") + '.png'
            f = open(file_name, 'wb')
            f.write(records[2])
            f.close()
            records[2] = file_name
            time.sleep(1)
        else:
            records[2] = "\n".join(records[2].strip().split("\n")[3:-1])
            if records[0] in ["Spectrum_Sprious"]:
                k = records[0] + records[1]
                v = records[2]
                global mid_dict
                mid_dict[k] = v
                records[2] = "Too much data, not display."
        records[3] = records[3].strftime("%Y-%m-%d %H-%M-%S")
    except:
        records = [testcase, modulation, "None", ""]
    finally:
        c.close()
        db.close()
        return records

def insert_result_to_db(table, modulation, testcase, result):
    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=database)
    sql = """describe %s;""" % table
    c = db.cursor()
    try:
        c.execute(sql)
    except:
        sql = """
        create table %s (
            id mediumint not null auto_increment,
            qam varchar(50) not null,
            testcase varchar(50) not null,
            result mediumblob,
            log mediumblob,
            time datetime not null,
            primary key (id)
        );
        """ % table
        c.execute(sql)
    try:
        if testcase in ['Jitter', 'Jitter on Tx sample PWM']:
            if os.path.exists(result):
                f = open(result, 'rb')
                b = f.read()
                f.close()
                sql = """insert into %s 
                (qam, testcase, result, log, time)
                values
                ('%s', '%s', %s, '',
                now());
                """ % (table, modulation, testcase, '%s')
                c.execute(sql, (MySQLdb.Binary(b)))
        else:
            sql = """
            insert into %s
            (qam, testcase, result, log, time)
            values
            ('%s', '%s', '%s', '',
            now());
            """ % (table, modulation, testcase, result)
            c.execute(sql)
    finally:
        db.commit()
        c.close()
        db.close()

def get_records_by_modulation_and_case(table, testcase, modulation):
    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=database)
    sql = """select result, log, time from %s
where testcase='%s' and qam='%s' order by id desc; """ \
    % (table, testcase, modulation)
    c = db.cursor()
    try:
        c.execute(sql)
        records = c.fetchall()
        def filter_record(record):
            record[0] = "\n".join(record[0].strip().split("\n")[3:-1])
            record[2] = record[2].strftime("%Y-%m-%d %H-%M-%S")
            return record
        records = map(lambda x: filter_record(list(x)), records)
    except:
        records = []
    finally:
        c.close()
        db.close()
        return records

def get_dut_information_records(prefix):
    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=database)
    sql = """select information, time from dut_information 
    where dut='%s' order by id desc; """ % prefix
    c = db.cursor()
    try:
        c.execute(sql)
        records = c.fetchall()
        def filter_record(record):
            record[0] = record[0].replace("\r", "")
            record[1] = record[1].strftime("%Y-%m-%d %H-%M-%S")
            return record
        records = map(lambda x: filter_record(list(x)), records)
    except:
        records = []
    finally:
        c.close()
        db.close()
        return records

def call_MsgBox(title, text):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle(title)
    msgBox.setText(text)
    msgBox.exec_()

def get_value(path, section, key):
    config = ConfigParser()
    config.read(os.path.join(base_path, path))
    return config.get(section, key)

class Result_update(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_result_update_dlg()
        self.ui.setupUi(self)
        self.__init_controls()
        self.__events()
        self.select = -1
        self.index = 0

    def insert_table(self, table, testcase, modulation):
        def insert_item(record):
            self.ui.records_table.insertRow(self.index)
            def insert_item_align_top(text):
                item = QtGui.QTableWidgetItem(text)
                item.setTextAlignment(QtCore.Qt.AlignTop)
                return item
            map(lambda x: self.ui.records_table.setItem(self.index, x, 
                insert_item_align_top(record[x])),
                xrange(3))
            self.ui.records_table.resizeRowsToContents()
            self.index = self.index + 1
        map(insert_item, 
            get_records_by_modulation_and_case(table, testcase, modulation))

    
    def __init_controls(self):
        self.ui.records_table.setColumnCount(3)
        headers = ("Result", "Log", "Time")
        self.ui.records_table.setHorizontalHeaderLabels(headers)
        column_width = [310, 300, 125]
        map(lambda x:
            self.ui.records_table.setColumnWidth(x, column_width[x]),
            xrange(3))
        self.ui.records_table.setSelectionMode(
            QtGui.QTableWidget.SingleSelection)
        self.ui.records_table.setSelectionBehavior(
            QtGui.QTableWidget.SelectRows)
        self.ui.records_table.setEditTriggers(
            QtGui.QTableWidget.NoEditTriggers)
        self.ui.records_table.setAlternatingRowColors(True)

    def __events(self):
        QtCore.QObject.connect(self.ui.button_ok,
            QtCore.SIGNAL("clicked()"), self.__ok)
        QtCore.QObject.connect(self.ui.button_cancel,
            QtCore.SIGNAL("clicked()"), self.__cancel)

    def __ok(self):
        self.select = self.ui.records_table.currentRow()
        self.close()

    def __cancel(self):
        self.select = -1
        self.close()

class Dut_Information(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_dut_information_dlg()
        self.ui.setupUi(self)
        self.__init_controls()
        self.__events()
        self.select = -1
        self.index = 0
    
    def __init_controls(self):
        self.ui.dut_information_table.setColumnCount(2)
        headers = ("Dut_Information", "Time")
        self.ui.dut_information_table.setHorizontalHeaderLabels(headers)
        column_width = [600, 150]
        map(lambda x:
            self.ui.dut_information_table.setColumnWidth(x, column_width[x]),
            xrange(2))
        self.ui.dut_information_table.setSelectionMode(
            QtGui.QTableWidget.SingleSelection)
        self.ui.dut_information_table.setSelectionBehavior(
            QtGui.QTableWidget.SelectRows)
        self.ui.dut_information_table.setEditTriggers(
            QtGui.QTableWidget.NoEditTriggers)
        self.ui.dut_information_table.setAlternatingRowColors(True)

    def insert_table(self, prefix):
        def insert_item(record):
            self.ui.dut_information_table.insertRow(self.index)
            def insert_item_align_top(text):
                item = QtGui.QTableWidgetItem(text)
                item.setTextAlignment(QtCore.Qt.AlignTop)
                return item
            map(lambda x: self.ui.dut_information_table.setItem(self.index, x, 
                insert_item_align_top(record[x])),
                xrange(2))
            self.ui.dut_information_table.resizeRowsToContents()
            self.index = self.index + 1
        map(insert_item, get_dut_information_records(prefix))
        
    def __events(self):
        QtCore.QObject.connect(self.ui.button_ok,
            QtCore.SIGNAL("clicked()"), self.__ok)
        QtCore.QObject.connect(self.ui.button_cancel,
            QtCore.SIGNAL("clicked()"), self.__cancel)

    def __ok(self):
        self.select = self.ui.dut_information_table.currentRow()
        self.close()

    def __cancel(self):
        self.select = -1
        self.close()

class Start(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.base_path = os.getcwd()
        self.__init_variables()
        self.__init_controls()
        self.__events()
        self.status = 0
        global base_path
        base_path = self.base_path
        clear_logfile_if_big_than_500k()

    def __init_controls(self):
        def get_sections(path):
            config = ConfigParser()
            config.read(os.path.join(self.base_path, path))
            l = config.sections()
            l.sort()
            return l
        self.ui.comboBox_platform.addItems(
            get_sections(r"configuration\Platform.ini"))
        self.ui.comboBox_frameformat.addItems(
            get_sections(r"configuration\FrameFormat.ini"))
        self.ui.comboBox_phymode.addItems(map(str,range(8)))
        self.ui.comboBox_testcase.addItems(case_mapper.keys())

        self.ui.table_vr.setColumnCount(4)
        headers = ("Testcase", "Modulation", "Result", "Time")
        self.ui.table_vr.setHorizontalHeaderLabels(headers)
        column_width = [100, 80, 730, 125]
        map(lambda x:
            self.ui.table_vr.setColumnWidth(x, column_width[x]),
            xrange(4))
        self.ui.table_vr.setSelectionMode(QtGui.QTableWidget.SingleSelection)
        self.ui.table_vr.setSelectionBehavior(QtGui.QTableWidget.SelectRows)
        self.ui.table_vr.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        self.ui.table_vr.setAlternatingRowColors(True)
        map(lambda x:
            self.ui.table_vr.horizontalHeader().setResizeMode(x, 
                QtGui.QHeaderView.Fixed), xrange(4))
        
        self.ui.button_dut_infor.setEnabled(False)
        self.ui.button_generate.setEnabled(False)
        self.ui.button_open_report.setEnabled(False)

    def __init_variables(self):
        self.image_path = ""

    def __events(self):
        QtCore.QObject.connect(self.ui.button_preview,
            QtCore.SIGNAL("clicked()"), self.__preview)
        QtCore.QObject.connect(self.ui.button_generate,
            QtCore.SIGNAL("clicked()"), self.__generate)
        QtCore.QObject.connect(self.ui.button_dut_infor,
            QtCore.SIGNAL("clicked()"), self.__update_dut_information)
        QtCore.QObject.connect(self.ui.button_open_report,
            QtCore.SIGNAL("clicked()"), self.__open_report)
        QtCore.QObject.connect(self.ui.table_vr,
            QtCore.SIGNAL("cellDoubleClicked (int,int)"), self.__update)
        QtCore.QObject.connect(self.ui.button_upload,
            QtCore.SIGNAL("clicked()"), self.__upload)
        QtCore.QObject.connect(self.ui.button_select_file,
            QtCore.SIGNAL("clicked()"), self.__select_file)

    def __preview(self):
        global base_path
        base_path = self.base_path
        self.platform = str(self.ui.comboBox_platform.currentText())
        self.frameformat = str(self.ui.comboBox_frameformat.currentText())
        prefix = get_value(r"configuration\Platform.ini",
            self.platform, "prefix")
        self.modulations = get_value(r"configuration\FrameFormat.ini",
            self.frameformat, "modulations").split(",")
        self.table = prefix + '_' + self.frameformat
        all_test_cases = case_seq
        if table_exist(self.table):
            global index
            index = 0
            self.ui.table_vr.clearContents()
            self.ui.table_vr.setRowCount(0)
            def insert_item(testcase, modulation):
                global index
                records = get_records_from_db(self.table, testcase, modulation)
                self.ui.table_vr.insertRow(index)
                map(lambda x: self.ui.table_vr.setItem(index, x, 
                    QtGui.QTableWidgetItem(records[x])),
                    xrange(4))
                self.ui.table_vr.resizeRowsToContents()
                index = index + 1
            map(lambda y: 
                map(lambda x: 
                    insert_item(y, x), 
                        self.modulations), 
                    all_test_cases)
            self.status = 1
            self.ui.button_dut_infor.setEnabled(True)
        else:
            self.ui.table_vr.clearContents()
            self.ui.table_vr.setRowCount(0)
            self.ui.button_dut_infor.setEnabled(False)
            call_MsgBox("No Result", 
                "No Result.\nPlease check platform and frame format")
        self.ui.button_generate.setEnabled(False)
        self.ui.button_open_report.setEnabled(False)

    def __update(self, row, column):
        testcase = self.ui.table_vr.item(row, 0).text()
        if str(testcase) in ["Spectrum_Sprious", 
            'Jitter', 'Jitter on Tx sample PWM']:
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle("!!!")
            msgBox.setText("Do you really really want to open it???");
            msgBox.setInformativeText(
                "It has too much data for spectrum result.");
            msgBox.setStandardButtons(
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            msgBox.setDefaultButton(QtGui.QMessageBox.Yes);
            ret = msgBox.exec_()
            if ret == QtGui.QMessageBox.No:
                return
        modulation = self.ui.table_vr.item(row, 1).text()
        if self.ui.table_vr.item(row, 2).text() != "None":
            dlg = Result_update()
            dlg.insert_table(self.table, testcase, modulation)
            dlg.exec_()
            if dlg.select > -1:
                result = dlg.ui.records_table.item(dlg.select, 0).text()
                testtime = dlg.ui.records_table.item(dlg.select, 2).text()
                if str(testcase) in ["Spectrum_Sprious"]:
                    global mid_dict
                    mid_dict[str(testcase) + str(modulation)] = str(result)
                    result = "Too much data, not display."
                self.ui.table_vr.setItem(
                    row, 2, QtGui.QTableWidgetItem(result))
                self.ui.table_vr.setItem(
                    row, 3, QtGui.QTableWidgetItem(testtime))
        else:
            call_MsgBox("No Result", "No Result!")

    def __update_dut_information(self):
        global dut_infor
        dlg = Dut_Information()
        prefix = get_value(r"configuration\Platform.ini",
            self.platform, "prefix")
        dlg.insert_table(prefix)
        dlg.exec_()
        if dlg.select > -1:
            dut_infor = str(
                dlg.ui.dut_information_table.item(dlg.select, 0).text())
        else:
            call_MsgBox("Warning", "Please select dut information")
        self.ui.button_generate.setEnabled(True)

    def __generate(self):
        if self.status == 1:
            global base_path, platform, frame_format, records, summary_index
            summary_index = 4
            base_path = self.base_path
            platform = str(self.platform)
            frame_format = str(self.frameformat)
            def get_record(row):
                return [str(self.ui.table_vr.item(row, 0).text()),
                    str(self.ui.table_vr.item(row, 1).text()),
                    str(self.ui.table_vr.item(row, 2).text())]
            records = filter(lambda x: x[2] != "None",
                    map(get_record, xrange(self.ui.table_vr.rowCount())))
            try:
                logger("New Generation\n")
                logger(platform)
                logger(frame_format)
                generate()
                global generation_warning
                if generation_warning != "":
                    call_MsgBox("Warning", generation_warning)
                    generation_warning = ""
                call_MsgBox("Finish", "Finish!")
                self.ui.button_open_report.setEnabled(True)
            except:
                logger("\n" + traceback.format_exc())
            finally:
                excel_close()

    def __open_report(self):
        excel_open()

    def __select_file(self):
        self.image_path = QtGui.QFileDialog.getOpenFileName(self, "Open Image",
            QtCore.QString(), "Image Files(*.png *.jpg *.bmp)")
        self.ui.textEdit_result.setText(self.image_path)

    def __upload(self):
        global base_path, platform, frame_format
        base_path = self.base_path
        platform = str(self.ui.comboBox_platform.currentText())
        frame_format = str(self.ui.comboBox_frameformat.currentText())
        phymode = str(self.ui.comboBox_phymode.currentText())
        testcase = str(self.ui.comboBox_testcase.currentText())
        prefix = get_value(r"configuration\Platform.ini",
            platform, "prefix")
        self.modulations = get_value(r"configuration\FrameFormat.ini",
            frame_format, "modulations").split(",")
        table = prefix + '_' + frame_format
        get_ff_mode()
        get_phymodes()
        get_modulations()
        try:
            modulation = get_modulation_from_phy(str(phymode))
        except:
            call_MsgBox("Error", "This FF doesn't have this phymode.")
            return
        if testcase in ['Jitter', 'Jitter on Tx sample PWM']:
            if self.image_path != "":
                result = self.image_path
            else:
                call_MsgBox("Error", "Please select result file ...")
                return
        else:
            result = str(self.ui.textEdit_result.toPlainText()).strip()
            if result == "":
                call_MsgBox("Error", "Please input result")
                return
        insert_result_to_db(table, modulation, testcase, result)
        call_MsgBox("Finish", "Finish!")

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = Start()
    myapp.show()
    sys.exit(app.exec_())
