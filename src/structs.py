#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic

class Structs(Basic):
  def __init__ (self):
    super(Structs, self).__init__()
    self.name = 'struct'
    self.fields = ['id', 'name', 'title', 'status', 'service', 'version', 'description', 'data']

