# -*- coding: utf-8 -*-
from __future__ import with_statement
import os
import re
from functional import partial

def gen(filename):
    pattern = ['MMU2H', '\|']
    fr = open(filename).readlines()
    def ismatch(p, c):
        m = re.search(p, c)
        return m
    new_f = filter(lambda x: filter(partial(ismatch, c=x), pattern), fr)
    with open('dd.txt', 'w') as fw:
        fw.writelines(new_f)
#pwd = os.getcwd()
#map(gen, filter(lambda x: 'txt' in x, os.listdir(pwd)))
gen('log_v.txt')
os.system('pause')
