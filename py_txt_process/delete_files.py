# -*- coding: utf-8 -*-
## Jerry Lu
"""delete file that line1 is 0
the file should not be read-only.
"""

import os
pwd = os.getcwd()
try:
    need_delete = []
    for filename in os.listdir(pwd):
        file_path = ''
        if filename[-3:] == 'txt':
            file_path = pwd + '\\' + filename
            print file_path
            txt = open(file_path)
            for i, line in enumerate(txt):
                if i == 1:
                    print line
                    if line == "0\n":
                        need_delete.append(file_path)
            txt.close()
    print need_delete
    for filename in need_delete:
        os.remove(filename)
    print "Done!"
except Exception, e:
    print e
    print "Error!"
    print "Check the directory name!"
finally:
    pass
