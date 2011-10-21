#192.168.110.200/getImage.html
import urllib
import urllib2
import re

html = urllib2.urlopen("http://192.168.110.200/getImage.html")
content = html.read()
p = re.compile('SRC="(.*)"')
li = re.findall(p, content)
print li[0]
print li[0].split('/')[-1]
#urllib.urlretrieve(li[0], li[0].split('/')[-1])
img = urllib2.urlopen(li[0]).read()
f = file('test.png', 'wb')
f.write(img)
f.close()
