# -*- coding: utf-8 -*-
# lreij
from __future__ import with_statement
from jinja2 import Environment, FileSystemLoader
import linecache
import re
import os.path

TMT_HANDLE = 'TMT_Handle.txt'
TEMPLATE_FOLDER = 'template'
FFD_FOLDER = 'ffd'
OUTPUT_PARAMETER_FOLDER = 'output_parameters'
SETUP_FOLDER = 'setup'

env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))
template = env.get_template('setup.tpl')

def get_line(f, n):
    return linecache.getline(f, n).rstrip()
 
def get_from_ffd(ffd_file, pattern, n):
    m = pattern.search(get_line(ffd_file, n))
    return m.group(1)

def get_item_from_ffd(ffd_file, n):
    p = re.compile(r'<item>(.*)</item>')
    return get_from_ffd(ffd_file, p, n)

def get_parameter_from_ffd(ffd_file, n):
    p = re.compile(r'value="(.*)"')
    return get_from_ffd(ffd_file, p, n)

def get_item_from_op(op_file, n):
    return get_line(op_file, n)

def get_value_from_op(op_file, n):
    p = re.compile(r': (.*)$')
    m = p.search(get_line(op_file, n))
    return m.group(1)

def get_phymodes(ffd_file):
    return [get_item_from_ffd(ffd_file, x) for x in xrange(7, 15)]

def read_ff_and_tmt():
    return open(TMT_HANDLE).readlines()

def get_ebn0s(ffd_file):
    if 'LDPC' not in ffd_file: index = 143
    else: index = 163
    return [get_item_from_ffd(ffd_file, x) 
            for x in xrange(index, index+8)]

def generate_per_phy(d, phy):
    if d['phymodes'][phy] == '0': return
    print d['ff'], d['phymodes'][phy]
    context = {}
    context['FF_name'] = d['ff']
    context['FF_mode'] = get_parameter_from_ffd(d['ffd'], 3)
    context['FF_market'] = get_parameter_from_ffd(d['ffd'], 4)
    context['QAM'] = get_item_from_ffd(d['ffd'], phy + 7)
    context['Channel_space'] = get_parameter_from_ffd(d['ffd'], 5)
    context['TMT_Handle'] = d['tmt']
    context['Phymode'] = phy
    context['FMX_Compsite_rate'] = get_value_from_op(d['op'], phy + 208)
    if 'A' in context['FF_market']:
        context['Bitrate'] = 1.544
    else: context['Bitrate'] = 2.048
    context['FF_Grossrate'] = get_item_from_op(d['op'], phy + 141)
    context['simulated_Ebn0_value'] = get_ebn0s(d['ffd'])[phy]
    d_start_ebn0 = {'CQPSK': 5, '4': 5, '16': 7, '32': 9, '64': 12, 
            '128': 15, '256': 18, '512': 20, '1024': 25}
    context['Ebn0_start_value'] = d_start_ebn0[context['QAM']]
    context['phymodes'] = ",".join([x for x in d['phymodes'] if x != '0'][::-1])
    context['FF_SymbolRate'] = get_item_from_op(d['op'], 138)
    context['Num_of_E1'] = get_item_from_op(d['op'], phy + 122)
    if 'LEG' in context['FF_mode']: setup = d['ff'] + '.txt'
    else: setup = d['ff'] + '_phy' + str(context['Phymode']) + '.txt'
    context['setup_file_name'] = setup
    with open(os.path.join(SETUP_FOLDER, setup), 'w') as f:
        f.write(template.render(context))

def generate_per_ff(ff, tmt):
    d = get_ffd_and_op_of_ff(ff, tmt)
    map(lambda x: generate_per_phy(d, x),
            xrange(0, 8))

def get_ffd_and_op_of_ff(ff, tmt):
    d = {}
    d['ff'] = ff
    d['tmt'] = tmt
    d['ffd'] = os.path.join(FFD_FOLDER, ff+'.xml')
    d['op'] = os.path.join(OUTPUT_PARAMETER_FOLDER, ff+'.txt')
    d['phymodes'] = get_phymodes(d['ffd'])
    return d

def generate():
    l = read_ff_and_tmt()
    map(lambda x: generate_per_ff(l[2*x].rstrip(), l[2*x+1].rstrip()), 
        xrange(0, len(l)/2))

if __name__ == '__main__':
    generate()
