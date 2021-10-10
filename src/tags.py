#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic

class Tags(Basic):
  def __init__ (self):
    super(Tags, self).__init__()
    self.name = 'tags'
    self.fields = ['id', 'name']
