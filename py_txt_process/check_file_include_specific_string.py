# -*- coding: utf-8 -*-

import os
pwd = os.getcwd()
try:
    li = map(lambda x: os.path.basename(x), 
            filter(lambda x: x[-8:-4] not in open(x).read(),
                map(lambda x: os.path.join(pwd, x),
                    filter(lambda x: 'hw0x' in x,
                        os.listdir(pwd)))))
    for x in li: print x
    print "Done!"
except Exception, e:
    print e 
finally:
    os.system('pause')
