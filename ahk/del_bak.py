# -*- coding: utf-8 -*-
## Jerry Lu 2010-10-13
"""use for delete the .bak file""" 

import os
pwd = os.getcwd()
#pwd = raw_input('Input The Directory:')
try:
    for filename in os.listdir(pwd):
        if filename[-4:] == '.bak':
            file_path = pwd + '\\' + filename
            os.remove(file_path)
    print "Done!"
except:
    print "Error!"
    print "Check the directory name!"
finally:
	os.system('pause')
