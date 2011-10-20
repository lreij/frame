# -*- coding: utf-8 -*-
## Jerry Lu <lreij@163.com>
"""Test for ftplib.
   parse FTP folders and files."""

import ftplib
import re

def return_file_list(ftp):
    path = ftp.pwd()
    print path
    f.write(path + '\n')
    list_file = ftp.nlst()
    for fileobject in list_file:
        if re.search('\.', fileobject):
            print '\t' + fileobject
            f.write('\t' + fileobject + '\n')
        else:
            ftp.cwd(path + '/' + fileobject)
            return_file_list(ftp)

ftp = ftplib.FTP('ftp.ni.com')
ftp.login()
f = file('F://test.txt', 'w')
return_file_list(ftp)
f.close()

