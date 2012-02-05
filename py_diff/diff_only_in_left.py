# -*- coding:utf-8 -*-
## lreij
""""""
import sys
import os

def help(Error=None):
    print "Usage: diff_only_in_left.py Folder1 Folder2"
    if Error:
        print Error
    sys.exit()

def diff(f1, f2):
    os.system("diff -ru %s %s" % (f1, f2))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        help()
    if not os.path.exists(sys.argv[1]):
        help("Error: Folder1 doesn't exist.")
    if not os.path.exists(sys.argv[2]):
        help("Error: Folder2 doesn't exist.")
    for root, dirs, files in os.walk(sys.argv[1]):
        for f in files:
            f1 = os.path.join(root, f)
            f2 = f1.replace(sys.argv[1], sys.argv[2])
            diff(f1, f2)
