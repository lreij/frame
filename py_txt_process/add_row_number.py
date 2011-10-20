# -*- coding:utf-8 -*-
## Jerry Lu <lreij@163.com>
"""add row number for plain text
    >>> python add_row_number.py xxx.txt
    """
import fileinput
for line in fileinput.input(inplace = True):
    line = line.rstrip()
    num = fileinput.lineno()
    print '%-40s # %2i' % (line, num)

