# -*- coding:utf-8 -*-
# lreij
"""auto mw"""
from pywinauto import application
import os
import re
import time

def run_single(d, product, ff, ffd, model):
    d['ProductComboBox'].Select(product)
    d['Frame FormatComboBox'].Select(ff)
    d['Frame Format Definition FileEdit'].SetText(ffd)
    d['ModelComboBox'].Select(model)
    time.sleep(1)
    d['CancelButton'].Click()

def sort_ff_label_from_cs():
    p = re.compile('\d{1,2}_CAX\d*?_\d-R\d\w\d{2}$')
    all_ff_old_label = map(lambda x: x.group(),
                filter(lambda x: x, 
                    map(p.search, 
                        open('cxc1726233_6.cs').readlines())))
    return all_ff_old_label

def ff_label_add_version(old):
    p = re.compile('^(.*R\d)(\w)(.*)$')
    def add_1(x):
        m = p.search(x)
        return m.group(1) + chr(ord(m.group(2)) + 1) + "01"
    all_ff_new_label = map(add_1, old)
    return all_ff_new_label

def x_by_y(pattern, label):
    p = re.compile(pattern)
    m = p.search(label)
    return d[m.group()]

def product_by_prefix(label):
    d = {'8': '',
        '15': '',
        '15': '',
        '15': ''}
    return x_by_y('^\d+', label)

def ffd_by_ff_num(label):
    d = {'8': '',
        '15': '',
        '15': '',
        '15': ''}
    return x_by_y('CAX\d{7}_\d', label)
   
def ff_by_ff_num(label):
    d = {'8': '',
        '15': '',
        '15': '',
        '15': ''}
    return x_by_y('CAX\d{7}_\d', label)

def input_by_new_label(label):
    return (product_by_prefix(label),\
            ff_by_ff_num(label),\
            ffd_by_ff_num(label),\
            "Mode")

def test():
    app = application.Application()
    app.connect_(title="New Configuration")
    dlg = app['New Configuration']
#print dlg.print_control_identifiers()
    run_single(dlg, "MINI_LINK_CN_TK", "CQPSK_R1_CS28_E",
            "F:\\Modem_wizard\\FFD\\ffd_CQPSK_R1_CS28_E_Komus.xml",
            "MasterModel_MINI_LINK_CN")

def run():
    app = application.Application()
    app.connect_(title="New Configuration")
    dlg = app['New Configuration']
    all_ff_label = sort_ff_label_from_cs()
    all_ff_new_label = ff_label_add_version(all_ff_label)
    def run_(*args):
        run_single(dlg,args[0],args[1],args[2],args[3])
    map(run_, map(input_by_new_label, all_ff_new_label))

if __name__ == '__main__':
     test()
#    run()
