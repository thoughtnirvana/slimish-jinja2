#!/usr/bin/env python
import os, sys
from jinja2 import Environment, FileSystemLoader
# Project imports.
from slimish_jinja import SlimishExtension

cur_dir = os.path.dirname(os.path.realpath(__file__))
demo_template = os.path.join(cur_dir, 'demo.slim')
env = Environment(loader=FileSystemLoader(cur_dir), extensions=[SlimishExtension])
env.slim_debug = True

with open(demo_template) as template:
    jinja_tmpl = env.get_template('demo.slim')
    users = [{'name': 'foo', 'last_name': 'bar'},
             {'name': 'bar', 'middle_name': 'baz'},
             {'name': 'baz'}]
    sys.stdout.write(jinja_tmpl.render(users=users, content='content', user_class='user_class'))
