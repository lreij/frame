import _globals
from t1 import t1
from t2 import t2
from t3 import t3

def print_():
    print '---'
    print 'a: ', _globals.a
    print 'b: ', _globals.b
    print 'c: ', _globals.c
    print 'd: ', _globals.d

if __name__ == '__main__':
    print_()
    t1()
    print_()
    t2()
    print_()
    t3()
    print_()
