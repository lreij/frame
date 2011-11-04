# -*- coding: utf-8 -*-
# lreij
import os

PATH = r'F:\doc'

def construct_cc_cmd(cmd, path):
    return cmd + ' "' + path +'"'

def search_all_view_private_elements(path):
    return os.popen(construct_cc_cmd('cleartool ls -r -view_only', 
        path)).readlines()

def search_view_private_elements_in_current_folder(path):
    return os.popen(construct_cc_cmd('cleartool ls -view_only', 
        path)).readlines()
    
def add_one_file(path):
    os.system(construct_cc_cmd('cleartool mkelem -nc -ci', path))

def search_view_private_elements_and_add_source_control(path):
    for root, dirs, files in os.walk(path):
        print root
        elements = search_view_private_elements_in_current_folder(root)
        if elements:
            os.system(construct_cc_cmd('cleartool checkout -nc', root))
            map(add_one_file, elements)
            os.system(construct_cc_cmd('cleartool checkin -nc', root))

if __name__ == '__main__':
    search_view_private_elements_and_add_source_control(PATH)
