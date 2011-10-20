# -*- coding: utf-8 -*-
from __future__ import with_statement
import linecache
import re

OP_PATH = r'Output_parameters_to_RL_sys_QAM_ADAPTIVE_R1_CS56_LDPC_E_MMU3A_test.txt'
CLI_PATH = r'template\CLI_template.txt'
SETUP_PATH = r'template\Setup_template.txt'
EQ_KI = [1, 2, 3, 4]
EQ_KP = [6, 7, 8, 9]
CR_KI = [2, 3, 4]
CR_KP = [6, 7, 8]
BEST_EQ = ['1616', '1616', '1616', '1616', '1616', '1616', '1616', '1616'] 
START_EBN0 = [5, 7, 10, 15, 17, 20, 23, 25]

def get_num_from_line(n):
    return linecache.getline(OP_PATH, n).rstrip()

def get_info_from_op_per_phy(n):
    qam = get_num_from_line(n+10)
    emb_qpsk = get_num_from_line(n+59)
    gross_rate = get_num_from_line(n+141)
    return (qam, emb_qpsk, gross_rate)

def get_info():
    return map(get_info_from_op_per_phy, xrange(8))

def get_setup_name():
    p = re.compile('QAM.*MMU3A')
    m = p.search(OP_PATH)
    return m.group()

def g_(s, p, t, n):
    return reduce(lambda x, y: x.replace(t[int(y)], p[int(y)]),
            [s] + map(str, range(n)))

def g_cli(s, p):
    t = ('@phy@', '@CR@', '@EQ@',)
    return g_(s, p, t, 3)

def g_setup(s, p):
    t = ('@start_ebn0@', '@gross_rate@',)
    return g_(s, p, t, 2)

def wf(s, c):
    with open('setups\\' + s, 'w') as f:
        f.write(c)

def write_to_file(sf, cf, s, c):
    map(lambda x: wf(x[0], x[1]), ((sf, s), (cf, c)))

def render(l, n):
    if int(l[n][1]) == 0: return
    cli = open(CLI_PATH).read()
    setup = open(SETUP_PATH).read()
    setup_file = get_setup_name() + '_test_phy' + str(n) + '_EBN0_P'
    p_setup = (str(START_EBN0[n]), str(int(float(l[n][2])*1000000)))
    cr = 2 * ('%i%i' % (CR_KI[1], CR_KP[1]))
    for i in range(4):
        for j in range(4):
            eq = 2 * ('%i%i' % (EQ_KI[j], EQ_KP[i]))
            p_cli = (str(n), cr, eq)
            pn = 'N%i' % (i*4+j)
            write_to_file(setup_file + pn + '.txt',
                    'CLI_' + setup_file + pn + '.txt',
                    g_setup(setup, p_setup),
                    g_cli(cli, p_cli))
    best_eq = BEST_EQ[n]
    for i in range(3):
        for j in range(3):
            cr = 2 * ('%i%i' % (CR_KI[j], CR_KP[i]))
            p_cli = (str(n), cr, best_eq)
            pn = 'M%i' % (i*4+j) 
            write_to_file(setup_file + pn + '.txt',
                    'CLI_' + setup_file + pn + '.txt',
                    g_setup(setup, p_setup),
                    g_cli(cli, p_cli))

def generate():
    [render(get_info(), i) for i in range(8)]
    #render(get_info(), 5)

if __name__ == '__main__':
    generate()
