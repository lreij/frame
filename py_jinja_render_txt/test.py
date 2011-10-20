# coding: UTF-8
# jinja2 test to render txt template.

from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('xxx.txt')
context = {'test': 'good test',
        'test1': 'not good test',
        'test2': 'very good test'}
print template.render(context)
