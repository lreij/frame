# -*- coding: utf-8 -*-
## Jerry Lu
"""Test for xml"""

import xml.etree.ElementTree as ET
import os

tree = ET.parse('C:\\Users\\luruijie\\Desktop\\vr_template.xml')
root = tree.getroot()
print root.attrib['author']
print root.attrib['ff_name']

i = 0
case_map = {}

for elem in root.findall('test_case'):
    case_map[elem.attrib['name']] = i
    i += 1
print case_map

print root[case_map['Hop']].attrib['mmu1']
#print root[case_map['Hop']].attrib
print root[case_map['E1']].attrib['pass']

#os.system('pause')
