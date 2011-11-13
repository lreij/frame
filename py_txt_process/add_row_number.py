# -*- coding:utf-8 -*-
## lreij
"""add row number for plain text
    >>> python add_row_number.py xxx.txt
    """
import fileinput
for line in fileinput.input(inplace = True):
    line = line.rstrip()
    num = fileinput.lineno()
    print '%-40s # %2i' % (line, num)

