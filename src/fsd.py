#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic

class FSD(Basic):
  def __init__ (self):
    super(FSD, self).__init__()
    self.name = 'fsd'
    self.fields = ['id', 'name', 'title', 'status', 'tags', 'services', 'description', 'link']

