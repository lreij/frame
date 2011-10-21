# -*- coding: utf-8 -*-
"""Add lines to txts.""" 
from __future__ import with_statement
import os

pwd = os.getcwd()
def add_line(i, line, add_content):
    if i in add_content.keys():
        return add_content[i] + '\n' + line 
    else:
        return line 
def gen(filename):
    file_path = pwd + '\\' + filename
    fr = open(file_path).readlines()
    add_content = {0: "hello",
            20: "world"}
    new_content = map(lambda (x, y): \
            add_line(x, y, add_content), 
            enumerate(fr))
    with open(file_path, 'w') as fw:
        fw.writelines(new_content)
map(gen, filter(lambda x: 'txt' in x, os.listdir(pwd)))
os.system('pause')
