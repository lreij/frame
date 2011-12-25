# -*- coding: utf-8 -*-
# lreij
# Usage: ff_config_generate.py > FrameFormat.ini

import re

if __name__ == '__main__':
    def get_ff(line):
        p_ff = re.compile(r"(CQPSK|QAM).*(_E|_A|E1)")
        m = p_ff.search(line)
        if m:
            return m.group(0)

    def get_modulation(ff):
        p_modulation = re.compile(r"(CQPSK|QAM\d*)")
        m = p_modulation.search(ff)
        if m:
            return m.group(0).replace('QAM', '')

    def get_phy_and_modulation(line):
        p_phy = re.compile( r"phy (\d) = (\d*)")
        m = p_phy.search(line)
        if m:
            return [m.group(1), m.group(2)]

    def get_product_number(line):
        p_number = re.compile( r"CAX\d*_\d")
        m = p_number.search(line)
        if m:
            return m.group(0).replace('CAX103', 
                'CAX 103 ').replace('_', '/')

    for line in open('ff.cs'):
        if 'MMU' in line:
            ff = get_ff(line)
            print '[' + ff + ']'
            if 'AD' not in ff:
                ff_mode = 'static'
                print 'phymodes=0'
                modulation = get_modulation(ff)
                print 'modulations=' + modulation
            else:
                ff_mode = 'admod'
                phymodes = "phymodes="
                modulations = "modulations="
        if 'phy' in line:
            phy_and_modulation = get_phy_and_modulation(line)
            phymodes += str(phy_and_modulation[0]) + ','
            modulations += str(phy_and_modulation[1]) + ','
        if 'CAX' in line:
            if 'DE' not in line:
                product_number = get_product_number(line)
                if ff_mode == 'admod':
                    print phymodes[:-1]
                    print modulations[:-1]
                print "product_number=" + product_number