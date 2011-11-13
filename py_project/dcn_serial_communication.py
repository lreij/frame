# -*- coding:utf-8 -*-
## lreij
from __future__ import with_statement
import visa
import time
import os
import re
import yaml
import serial
import binascii

class HP3784a:
    def __init__(self, gpib_port):
        port = "GPIB0::%i::INSTR" % gpib_port 
        self.__a = visa.instrument(port)
    def __del__(self):
        print 'close HP3784A GPIB port'
        self.__a.close()
    def set_up(self):
        print 'set up HP3784A'
        self.__a.write("TIF 3")
        self.__a.write("RCF 3")
        self.__a.write("RIF 5")
        self.__a.write("BIL 1")
        self.__a.write("TPT 1")
        self.__a.write("RPT 3")
        self.__a.write("EAD 0")
        self.__a.write("TCL 2")
        self.__a.write("RCP 1")
    def get_ber_zero(self):
        print 'check ber level:'
        self.__a.write("RSB? 2")
        rsp = self.__a.read()
        p_ber = re.compile('\d*$')
        ber = re.findall(p_ber, rsp)[0]
        print '\tlevel is %s' % ber 
        if ber != '0':
            return False
        return True
    def start_bert(self):
        self.__a.write("STR")
    def stop_bert(self):
        self.__a.write("STP")
    def get_info(self):
        self.__a.write("ID?")
        print self.__a.read()
    def get_tx_clock(self):
        print 'get Tx clock'
        self.__a.write("TCF?")
        rsp = self.__a.read()
        p_f = re.compile('\d*$')
        return (int(re.findall(p_f, rsp)[0]) / 1000)
    def get_rx_clock(self):
        print 'get Rx clock'
        self.__a.write("RSF?")
        rsp = self.__a.read()
        p_f = re.compile('\d*$')
        r_c = int(re.findall(p_f, rsp)[0]) / 1000
        print '\t' + str(r_c) + 'kHz'
        return r_c

class A33250:
    def __init__(self, gpib_port):
         port = "GPIB0::%i::INSTR" % gpib_port 
         self.__a = visa.instrument(port)
    def __del__(self):
        print 'close A33250 GPIB port'
        self.__a.close()
    def set_freq(self, freq):
        print 'set A33250 Freq %f kHz' % freq
        self.__a.write("APPL:SQU %f KHZ" % freq)
        time.sleep(3)
    def get_info(self):
        self.__a.write("*IDN?")
        print self.__a.read()

def s_hex(s_asii):
    return binascii.a2b_hex(s_asii)

class rs232:
    def __init__(self, port, baudrate):
        print 'init serial port'
        self.__s = serial.Serial(port, baudrate)
        time.sleep(5)
    def __del__(self):
        print 'release serial port'
        self.__s.close()
    def write(self, content):
        self.__s.write(s_hex(content))
        time.sleep(5)
    def read(self):
        self.__s.read()
    def change_baudrate(self, br):
        self.__s.baudrate = br
        time.sleep(5)
    def set_ff(self, ff):
        print "set ff"
        cmd = '5AA5C33C000000300000002400000000000000000000000001000016000000010000000000000000000000%sA55A3CC3' % (ff.upper())
        self.write(cmd)
    def set_if_loop_on(self):
        print "set if loop on"
        cmd = '5AA5C33C0000002D0000002100000000000000000000000001000002000000010000000005B35A3801A55A3CC3'
        self.write(cmd)
    def set_if_loop_off(self):
        print "set if loop off"
        cmd = '5AA5C33C0000002D0000002100000000000000000000000001000002000000010000000005B35A3800A55A3CC3'
        self.write(cmd)
    def set_phy_mod(self, phy):
        print "set phy mode: " + str(phy)
        cmd1 = '5AA5C33C0000003500000029000000000000000000000000FF01000800000001000000000E2A84E290003A2C02000100FFA55A3CC3'
        cmd2 = '5AA5C33C0000003500000029000000000000000000000000FF01000800000001000000000E2A853090003A1002000%i00FFA55A3CC3' % phy
        cmd3 = '5AA5C33C0000003500000029000000000000000000000000FF01000800000001000000000E2A856E90003A3802001%i00FFA55A3CC3' % phy
        cmd = cmd1 + cmd2 + cmd3
        self.write(cmd)
    def set_e1(self):
        print 'set e1'
        cmd1 = '5AA5C33C0000003500000029000000000000000000000000FF01000800000001000000000E34B709900001200200010001A55A3CC3'
        cmd2 = '5AA5C33C0000003500000029000000000000000000000000FF01000800000001000000000E34B747900001AC02006100FFA55A3CC3'
        cmd3 = '5AA5C33C0000003500000029000000000000000000000000FF01000800000001000000000E34B786900001B002000100FFA55A3CC3'
        cmd4 = '5AA5C33C0000003500000029000000000000000000000000FF01000800000001000000000E34B7C4900001A00200F000FFA55A3CC3'
        cmd5 = '5AA5C33C0000003500000029000000000000000000000000FF01000800000001000000000E34B812900001A402000B00FFA55A3CC3'
        cmd = cmd1 + cmd2 + cmd3 + cmd4 + cmd5
        self.write(cmd)
    def set_dcn(self):
        print 'set dcn'
        cmd1 = '5AA5C33C0000003500000029000000000000000000000000FF01000800000001000000000E313BE1900001200200010001A55A3CC3'
        cmd2 = '5AA5C33C0000003500000029000000000000000000000000FF01000800000001000000000E313C20900001AC02006100FFA55A3CC3'
        cmd3 = '5AA5C33C0000003500000029000000000000000000000000FF01000800000001000000000E313C5E900001B002000500FFA55A3CC3'
        cmd4 = '5AA5C33C0000003500000029000000000000000000000000FF01000800000001000000000E313C9C900001A00200F000FFA55A3CC3'
        cmd5 = '5AA5C33C0000003500000029000000000000000000000000FF01000800000001000000000E313CEA900001A402000B00FFA55A3CC3'
        cmd = cmd1 + cmd2 + cmd3 + cmd4 + cmd5
        self.write(cmd)
    def get_mse(self):
        print "get mse"
        pass 

def wait_s(s):
    hp.stop_bert()
    time.sleep(2)
    hp.start_bert()
    time.sleep(s)

def write_to_file(content):
    with open('result.txt', 'a') as result:
        print content
        result.write(content)

def dcn_go():
    dcn_f = int((hp.get_rx_clock() + 20) / 64) * 64    
    print 'the init freq is %i' % dcn_f
    a.set_freq(dcn_f)
    time.sleep(5)
    r_f = dcn_f       

    def get_f(freq_l, freq_r, what):
        a.set_freq(dcn_f)
        freq_m = 0.5 * (freq_l + freq_r)
        if (freq_r - freq_l) < 0.000001: 
            return freq_m
        a.set_freq(freq_m)
        wait_s(30)
        if hp.get_ber_zero():
            if what == 'h':
                return get_f(freq_m, freq_r, what)
            else:
                return get_f(freq_l, freq_m, what)
        else:
            if what == 'h':
                return get_f(freq_l, freq_m, what)
            else:
                return get_f(freq_m, freq_r, what)

    print '\nH freq'
    while True:
        r_f += 0.1
        a.set_freq(r_f)
        wait_s(20)
        if not hp.get_ber_zero():
            break
    l_f = r_f - 0.1
    a.set_freq(dcn_f)
    wait_s(5)
    f_h = get_f(l_f, r_f, 'h')

    print '\nL freq'
    l_f = dcn_f
    while True:
        l_f -= 0.1
        a.set_freq(l_f)
        wait_s(20)
        if not hp.get_ber_zero():
            break
    r_f = l_f + 0.1
    a.set_freq(dcn_f)
    wait_s(5)
    f_l = get_f(l_f, r_f, 'l')

    content = 'Low freq: ' + str(f_l) + '\nHigh freq: ' + str(f_h) + '\n'
    write_to_file(content) 
                                            
if __name__ == '__main__':
    try:
        with open('dcn.txt', 'r') as init_file:
            content = init_file.read()
            dcn_init = yaml.load(content)

        hp = HP3784a(dcn_init['HP3784A'])
        a = A33250(dcn_init['A33250'])    
        m = rs232(dcn_init['MMU'] - 1, 115200)
        hp.get_info()
        a.get_info()
        hp.set_up()
        
        for tmt in dcn_init['Static']:
            if tmt is None:
                continue
            write_to_file('TMT: %s\n' % tmt)
            m.set_ff(tmt)
            m.set_dcn()
            m.set_if_loop_on()
            time.sleep(5)
            dcn_go()

        for tmt in dcn_init['Admod']:
            if tmt is None:
                continue
            write_to_file('TMT: %s\n' % tmt.keys()[0])
            m.set_ff(tmt.keys()[0])
            m.set_dcn()
            m.set_if_loop_on()
            for phy in tmt[tmt.keys()[0]]:
                write_to_file('Phy mode: %s\n' % phy)
                m.set_phy_mod(phy)
                time.sleep(5)
                dcn_go()

    except Exception, e:
        print e
    finally:
        os.system('pause')