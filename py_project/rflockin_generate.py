# -*- coding: utf-8 -*-
from __future__ import with_statement
from jinja2 import Environment, FileSystemLoader
import linecache
import re
import os.path

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('rflockin.txt')

FFD_FOLDER = 'PUMA1'
SETUP_FOLDER = 'setup'

def read_ff_and_tmt():
    return open(r'TMT_Handle.txt').readlines()

def get_ff_from_filename(filename):
    p = re.compile(r'ffd_(.*)_PUMA1.xml')
    m = p.search(filename)
    return m.group(1)

def get_line(ffd_file, n):
    return linecache.getline(os.path.join(FFD_FOLDER, ffd_file), n).rstrip()

def get_num_from_line(ffd_file, i):
    p = re.compile(r'<item>(.*)</item>')
    m = p.search(get_line(ffd_file, i))
    return m.group(1)

def get_phymodes(ffd_file):
    return [get_num_from_line(ffd_file, x) for x in xrange(7, 15)]

def get_ebn0s(ffd_file):
    if 'LDPC' not in ffd_file: index = 143
    else: index = 163
    return [get_num_from_line(ffd_file, x) 
            for x in xrange(index, index+8)]

def generate_per_phy(ffd, tmt, phymodes, i):
    ff = get_ff_from_filename(ffd)
    print ff
    if phymodes[i] == '0':
        return
    if 'ADA' not in ffd:
        setup = 'MMU3A_' + ff + '_rflockin.txt'
    else: 
        setup = 'MMU3A_' + ff + '_phy' + str(i) + '_rflockin.txt'
    if '_A_' not in ffd:
        bitrate = 2048000
    else:
        bitrate = 1544000
    context = { 'QAM': phymodes[i],
            'BITRATE': bitrate,
            'SIMULATED': get_ebn0s(ffd)[i],
            'TMT': tmt,
            'PHY': i
            }
    with open(os.path.join(SETUP_FOLDER, setup), 'w') as f:
        f.write(template.render(context))

def generate_per_ff(ffd, tmt):
    phymodes = get_phymodes(ffd)
    map(lambda x: generate_per_phy(ffd, tmt, phymodes, x),
            xrange(0, 8))

def generate():
    l = read_ff_and_tmt()
    map(lambda x: generate_per_ff(l[2*x].rstrip(), l[2*x+1].rstrip()), 
        xrange(0, len(l)/2))

if __name__ == '__main__':
    generate()
