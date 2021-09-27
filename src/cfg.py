#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
from .basic import Basic

class Cfg():
  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(ELog, cls).__new__(cls)
      return cls.instance

  def __init__ (self):
    super(ELog, self).__init__()
    self.name = 'cfg'
    self.fields = ['key', 'data']

  def getValue(self, name):
    return self.m.get(name, '')
