# -*- coding: utf-8 -*-
# lreij
import os

PATH = r'F:\doc\mmu'
def add_one_file(path):
    os.system('cleartool mkelem -nc ' + path)
    #print path

def add_list(base, l):
    map(lambda x: add_one_file(os.path.join(base, x)), l)

def add_entire_folder_to_source_control():
    for root, dirs, files in os.walk(PATH):
        print root
        os.system('cleartool checkout -nc ' + root)
        map(lambda x: add_list(root, x), (dirs, files))
        os.system('cleartool checkin -nc ' + root)

if __name__ == '__main__':
    add_entire_folder_to_source_control()
