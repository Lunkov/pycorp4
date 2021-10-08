#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic

class Domains(Basic):
  def __init__ (self):
    super(Domains, self).__init__()
    self.name = 'domains'
    self.fields = ['id', 'name', 'status', 'layer', 'link', 'comment']

