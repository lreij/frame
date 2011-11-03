# -*- coding: utf-8 -*-
import os

PATH = r'F:\doc'
def walk_through_dir():
    for root, dirs, files in os.walk(PATH):
        print root
        print dirs
        print files 

if __name__ == '__main__':
    run()
