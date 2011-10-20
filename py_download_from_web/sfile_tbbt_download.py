# -*- coding: utf-8 -*-
## Jerry Lu <lreij@163.com>
"""Test for BeautifulSoup.
   Download the TBBT from sfile."""

from BeautifulSoup import BeautifulSoup
import urllib2
import re
import os
import webbrowser

home_page = urllib2.urlopen("http://bbs.sfileydy.com/forumdisplay.php?fid=272")
soup = BeautifulSoup(home_page)
u115_link_re = "(http://u.*?)"
i = 0
for page_link_str in soup.findAll('th'):
    if re.search(r'Bang', str(page_link_str)):
        if not re.search(r'720', str(page_link_str)):
            page_link = "http://bbs.sfileydy.com/"
            page_link += page_link_str.contents[4].contents[0]['href']
            print page_link
            page = urllib2.urlopen(page_link)
            soup_1 = BeautifulSoup(page)
            u115_link = soup_1.findAll(text = re.compile(u115_link_re))
            if u115_link != []:
                webbrowser.open(u115_link[0])
                i += 1
print '%s links' % i                
os.system('pause')
