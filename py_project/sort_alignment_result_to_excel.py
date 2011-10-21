# -*- coding: utf-8 -*-

import re
from functional import partial
regex = ['(.*)_MMU', 'is (\d*\.\d*)ns']
pattern = map(re.compile, regex)
def get_m(p, c):
    m = re.search(p, c)
    if m:
        return m.group(1)
    return None
match = map(lambda x: partial(get_m, p=x), pattern)
file_read = open('result_hot.txt').readlines()
func_read = lambda fn: \
        filter(lambda x: x,
            map(lambda x: fn(c=x), file_read))
match_list = map(func_read, match)
file_write = open('ok.txt', 'w')
func_write = lambda (x, y): \
        file_write.writelines(y + '\t'
                + match_list[1][2*x] + '\n\t'
                + match_list[1][2*x+1] + '\n')
map(func_write, enumerate(match_list[0]))
file_write.close()
