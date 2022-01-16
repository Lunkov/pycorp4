#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
from .basic import Basic
from .elog import ELog

class Links(Basic):
  def __init__ (self):
    super(Links, self).__init__()
    self.name = 'servicelinks'
    self.ids = ['item_from', 'item_to', 'type', 'tags', 'link', 'status', 'description']
    self.fields = ['item_from', 'item_to', 'type', 'status', 'tags', 'link', 'domain', 'description', 'comment']
    self.f_index = ['type', 'status', 'item_from', 'item_to', 'tags']

  def calc(self, services):
    elog = ELog()
    for i, v in self.data.items():
      s1 = services.getItem(v.get('item_from', ''))
      s2 = services.getItem(v.get('item_to', ''))
      if s1 is None:
        print("ERR: service '%s' not found " % v.get('item_from', ''))
        elog.log("LINK_ERROR", "ERR: service '%s' not found " % v.get('item_from', ''), v.get('item_from', ''), '')
        continue
      if s2 is None:
        print("ERR: service '%s' not found " % v.get('item_to', ''))
        elog.log("LINK_ERROR", "ERR: service '%s' not found " % v.get('item_to', ''), v.get('item_to', ''), '')
        continue
      if s1.get('domain', 's1') == s2.get('domain', 's2'):
        self.data[i]['domain'] = s1.get('domain', '')
