#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
from .basic import Basic

class API(Basic):
  def __init__ (self):
    super(API, self).__init__()
    self.name = 'api'
    self.fields = ['id', 'name', 'title', 'service', 'method', 'api', 'status', 'description', 'link', 'linkin']

  def addItem(self, name, properties):
    properties['linkin'] = hashlib.md5(("%s.%s.%s" % (properties.get('service', ''), properties.get('method', ''), properties.get('api', ''))).encode('utf-8')).hexdigest()
    super(API, self).addItem(name, properties)
  
  def graphWULF(self, G):
    for i, v in self.m.items():
      G.add_node(i)
      G.add_edge(i, v['service'])
    for n, data in G.nodes(data=True):
      if n in self.m:
        data['size'] = 0.2

  def graphVIZ(self, G):
    for i, v in self.m.items():
      G.add_node(i, label = v['title'], color = 'yellow', size = 5)
      G.add_edge(i, v['service'], weight = 0.2)
