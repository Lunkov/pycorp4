#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic
    
class Nodes(Basic):
  def __init__ (self):
    super(Nodes, self).__init__()
    self.name = 'nodes'
    self.fields = ['id', 'name', 'title', 'domain', 'type', 'status', 'layer', 'tags', 'description', 'mem', 'cpu', 'hdd', 'net']


