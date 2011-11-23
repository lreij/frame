# -*- coding: utf-8 -*-
# lreij
import MySQLdb

old = r""
new = r""

f = open(old, 'rb')
b = f.read()
f.close()
db = MySQLdb.connect(db="test_labview")
c = db.cursor()
c.execute("""insert into result 
    (phy, result, log, time) 
    values 
    ('QAM16',
    %s, 
    'ddd', 
    now());""", (MySQLdb.Binary(b)))
db.commit()
c.execute("""select * from result where id=6""")
d = c.fetchone()[2]
f = open(new, 'wb')
f.write(d)
f.close()
