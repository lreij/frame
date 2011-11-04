# -*- coding: utf-8 -*-
# lreij
import os

PATH = r'F:\doc'
PATHS = []

def construct_cc_cmd(cmd, path):
    return cmd + ' "' + path +'"'

def add_one_file(path):
    os.system(construct_cc_cmd('cleartool mkelem -nc -ci', path))

def add_list(root, l):
    map(lambda x: add_one_file(os.path.join(root, x)), l)

def add_entire_folder_to_source_control(path):
    for root, dirs, files in os.walk(path):
        print root
        os.system(construct_cc_cmd('cleartool checkout -nc', root))
        # if add folders and files
        #map(lambda x: add_list(root, x), (dirs, files))
        # if only add files
        map(lambda x: add_list(root, x), (files,))
        os.system(construct_cc_cmd('cleartool checkin -nc', root))

if __name__ == '__main__':
    #add_entire_folder_to_source_control(PATH)
    map(add_entire_folder_to_source_control, PATHS)
