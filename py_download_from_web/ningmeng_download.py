# -*- coding:utf-8 -*-
## Jerry Lu <lreij@163.com>
"""download the mp3 from Ningmeng.name"""
import urllib
import re

download_sum_url = []
for i in range(202, 203): #277
    page_url = 'http://www.ningmeng.name/post-' + str(i) + '.html'    
    page = urllib.urlopen(page_url)
    page_content = page.read()
    u115_p = re.compile('(http://u.115.com.*?)"')
    u115_url = re.findall(u115_p, page_content)
    if u115_url == []:
        continue
    print u115_url
    u115_page = urllib.urlopen(u115_url[0])    
    u115_content = u115_page.read()
    download_p = re.compile('(http://\d\d.bak.*?)"')
    download_url = re.findall(download_p, u115_content)
    if download_url == []:
        continue
    print download_url
# if download the file using python
#    urllib.urlretrieve(download_url[0])
    download_sum_url.extend(download_url)
        
save_file_str = ''
save_file_str = '<html><head><title>Download Link Lists</title></head><body><a href="'
str_temp = '">link</a><br><a href="'.join(url for url in download_sum_url)
save_file_str += str_temp
save_file_str += '">link</a></body></html>'

f = file('D://links.html', 'w')
f.write(save_file_str)
f.close()

print "\n\n\nDone!"
