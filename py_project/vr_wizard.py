# -*- coding:utf-8 -*-
## lreij
import os
import shutil
import sqlite3

def logger(func):
    """print log"""
    def log_it(*args, **argv):
        """wrapper"""
        try:
            print func.__doc__,
            value = func(*args, **argv)
            print "\t\t\t\t\tDone"
        except Exception, e:
            print
            print e
            os.system('pause')
        return value
    return log_it

@logger
def read_config(config_file):
    """read config file"""
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.readfp(open(config_file))
    d = {}
    d['author'] = cfg.get("VR", "Author")
    d['ff'] = cfg.get("VR", "FrameFormat")
    d['ff_pn'] = cfg.get("VR", "FrameFormat_Product_Number")
    d['phy0'] = cfg.get("VR", "PHY0")
    d['phy1'] = cfg.get("VR", "PHY1")
    d['phy2'] = cfg.get("VR", "PHY2")
    d['phy3'] = cfg.get("VR", "PHY3")
    d['phy4'] = cfg.get("VR", "PHY4")
    d['phy5'] = cfg.get("VR", "PHY5")
    d['phy6'] = cfg.get("VR", "PHY6")
    d['phy7'] = cfg.get("VR", "PHY7")
    d['dut'] = cfg.get("VR", "DUT")
    d['dut_hw'] = cfg.get("VR", "DUT_HW_Number")
    d['dut_sw'] = cfg.get("VR", "DUT_SW_Number")
    d['rs'] = cfg.get("VR", "RS")
    return d

db = sqlite3.connect("model.db")
config = read_config("config.ini")
phy = []
for k, v in config.items():
    if 'phy' in k:
        if v != '':
            phy.append(k)
phy.sort()

def execute_sql(sql):
    c = db.cursor()
    c.execute(sql)
    db.commit()
    c.close()

def fetch_item(db_name, case, py):
    c = db.cursor()
    sql = """select %s from %s where phy = "%s"
    """ % (case, db_name, py)
    c.execute(sql)
    item = c.fetchone()
    return item

@logger
def create_table(db_name):
    """create table """
    print db_name,
    ff = config['ff']
    c = db.cursor()
    if 'ADA' in ff:
        sql = """create table %s 
        (phy text primary key, mse text, hop text, PhyModeSwitch text,
        delay text, equipment_dely text, tx_power text,
        RFLockIn text, Signature text, RPS text, dcn text,
        num_of_e1 text, alignment_delay text);""" % (db_name)
        for py in phy:
            sql += """insert into %s
            (phy) values ("%s");""" % (db_name, py)
    else:
        sql = """create table %s 
        (phy text primary key, mse text, hop text,
        delay text, equipment_dely text, tx_power text,
        RfLockIn text, Signature text, RPS text, dcn text,
        num_of_e1 text, alignment_delay text);""" % (db_name)
        sql += """insert into %s 
        (phy) values ("static");""" % (db_name)
    c.executescript(sql)
    db.commit()
    c.close()

@logger
def join_txt():
    """join txt files"""
    all_text = ''
    for filename in os.listdir('.\\input'):
        if filename[-3:] == 'txt':
            all_text += open('.\\input\\' + filename).read()
            all_text += '\n'
    return all_text

@logger
def sort_txt_to_db(txt_result):
    """sort result to database"""
    ff = config['ff']
    li = txt_result.split('\n')
    for i, line in enumerate(li):
        if line == "-------------------------------------":
            if li[i-2] == "" or 'EbN0' in li[i-2] or
                li[i+1] == "":
                continue
            if ff in li[i-1]:
                col = li[i-2]
                j = i + 2
                while True:
                    if li[j] == "":
                        break
                    j = j + 1
                result = '\n'.join(li[i+1:j])
                if 'ADA' in ff:
                    import re
                    p = re.compile('phy\d')
                    phy = p.findall(li[i-1])[0]
                else:
                    phy = 'static'
                sql = """update model set %s = "%s"
                where phy = "%s"
                """ % (col, result, phy)
                execute_sql(sql)
                sql = """update result set %s = "%s"
                where phy = "%s"
                """ % (col, li[j+1], phy)
                execute_sql(sql)

@logger
def gc():
    """clear database"""
    db.cursor().execute("drop table model")
    db.cursor().execute("drop table result")

@logger
def close_db():
    """close database"""
    db.close()

import win32com
from win32com.client import Dispatch

class word:
    def __init__(self, path):
        self.__app = win32com.client.Dispatch('Word.Application')
        self.__app.Visible = 0
        self.__app.DisplayAlerts = 0
        self.__app.Documents.Open(path)

    def __del__(self):
        self.__app.Documents.Save()
        self.__app.Documents.Close()
        self.__app.Quit()

    def insert_string(self, position, content):
        sel = self.__app.Selection
        sel.WholeStory() 
        sel.Find.ClearFormatting()
        sel.Find.Replacement.ClearFormatting()
        sel.Find.Execute(position)
        sel.Text = content

    def replace_string(self, old_string, new_string):
        sel = self.__app.Selection
        sel.Find.ClearFormatting()
        sel.Find.Replacement.ClearFormatting()
        sel.Find.Execute(old_string, False, False, False, False, \
        False, True, 1, True, new_string, 2) 

    def paste_chart(self, position):
        sel = self.__app.Selection
        sel.WholeStory()
        sel.Find.ClearFormatting()
        sel.Find.Execute(position)
        sel.Paste()        

    def insert_picture(self, position, picture):
        sel = self.__app.Selection
        sel.WholeStory()
        sel.Find.ClearFormatting()
        sel.Find.Execute(position)         
        sel.InlineShapes.AddPicture(picture)

def po(path):
    """generate path for office program"""
    return os.path.join(os.getcwd(), path)

def vr_generate():
    class VR(object):
        def __init__(self):
            pass

        def __del__(self):
            pass

        @logger
        def __create_dir_and_files(self):
            """create result dir and files"""
            self.ff_dir = config['ff_pn'].replace('/', '_').replace(' ', '') 
            self.ff_path = '.\\output\\' + self.ff_dir
            os.mkdir(self.ff_path)
            self.ff_10267 = '10267-' + self.ff_dir + 'EN.doc'
            self.ff_10265 = '10265-' + self.ff_dir + 'EN.zip'
            shutil.copyfile('.\\template\\template.doc', os.path.join(self.ff_path, self.ff_10267))
            self.CIR =  self.ff_path + os.sep + 'CIR'
            os.mkdir(self.CIR)
            self.Ebn0_path =  self.ff_path + os.sep + 'Ebn0'
            os.mkdir(self.Ebn0_path)
            self.Spectrum_path =  self.ff_path + os.sep + 'Spectrum&Spurious'
            os.mkdir(self.Spectrum_path)

        @logger
        def __update_common(self, r):
            """update report common information"""
            import time
            r.replace_string('#product_number#', config['ff_pn'])
            r.replace_string('#Author#', config['author'])
            r.replace_string('#Date#', time.strftime('%Y-%m-%d', time.localtime()))
            r.replace_string('#RS#', config['ff_pn'][2:-2])
            r.replace_string('#RS_R#', config['rs'])
            r.replace_string('#SW#', config['dut_sw'])
            r.replace_string('#HW#', config['dut_hw'])
            r.replace_string('#DUT#', config['dut'])

        def generate(self):
            self.__create_dir_and_files()
            r = word(po(os.path.join(self.ff_path, self.ff_10267)))
            self.__update_common(r)

            class Case(object):
                """case"""
                def __init__(self, r):
                    self.vr = r

                def go(self):
                    """an interface"""
                    pass

                def __fetch_item_and_result(self, c, py):
                    item = fetch_item('model', c, py)
                    result = fetch_item('result', c, py)
                    if item[0] is None or result[0] is None:
                        return None
                    return (item[0], result[0])

                def get_content(self, c):
                    content = ''
                    result = ''
                    if 'ADA' in config['ff']:
                        for py in phy:
                            _set = self.__fetch_item_and_result(c, py)
                            if _set is not None:
                                content += "%s:\r%s\r"\
                                        % (config[py], _set[0])
                                if _set[1] != "Pass":
                                    result = _set[1]
                    else:
                        _set = self.__fetch_item_and_result(c, 'static')
                        if _set is not None:
                            content = _set[0]
                            if _set[1] != "Pass":
                                result = _set[1]
                    if result ==  '':
                        result = 'Pass'
                    return (result, content)

            class PhyModeSwitch(Case):
                def __init__(self, r):
                    super(PhyModeSwitch, self).__init__(r)

                @logger
                def go(self):
                    """PhyModeSwitch"""
                    if 'ADA' in config['ff']:
                        _set = self.get_content("")
                        self.vr.replace_string('#Phy_mods#', _set[0])
                        self.vr.insert_string('#Phy_mods_result#', _set[1])
                    else:
                        self.vr.replace_string('#Phy_mods#', 'N/A')
                        self.vr.insert_string('#Phy_mods_result#', 'N/A')
 #           PhyModeSwitch(r).go()

            class rf_lockin(Case):
                def __init__(self, r):
                    super(rf_lockin, self).__init__(r)

                @logger
                def go(self):
                    """RFLockin"""
                    _set = self.get_content("RFLockIn")
                    self.vr.replace_string('#Rf_lockin#', _set[0])
                    self.vr.insert_string('#Rf_lockin_result#', _set[1])
            rf_lockin(r).go()
            
            class Signature(Case):
                def __init__(self, r):
                    super(Signature, self).__init__(r)

                @logger
                def go(self):
                    """Signature"""
                    _set = self.get_content("Signature")
                    self.vr.replace_string('#Signature#', _set[0])
                    self.vr.insert_string('#Signature_result#', _set[1])
            Signature(r).go()

            class RPS(Case):
                def __init__(self, r):
                    super(RPS, self).__init__(r)

                @logger
                def go(self):
                    """RPS"""
                    _set = self.get_content("RPS")
                    self.vr.replace_string('#Rps#', _set[0])
                    self.vr.insert_string('#Rps_result#', _set[1])
            RPS(r).go()

    report = VR()
    print """\n\tCase"""
    report.generate()

def flow():
    gc()
    create_table('model')
    create_table('result')
    sort_txt_to_db(join_txt())
    vr_generate()
   # gc()
    close_db()
    

if __name__ == "__main__":
    flow()
