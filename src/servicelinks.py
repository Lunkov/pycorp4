#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
from .basic import Basic
from .elog import ELog

class ServiceLinks(Basic):
  def __init__ (self):
    super(ServiceLinks, self).__init__()
    self.name = 'servicelinks'
    self.ids = ['service_from', 'service_to', 'tags', 'link', 'status', 'description']
    self.fields = ['service_from', 'service_to', 'status', 'tags', 'link', 'domain', 'description', 'comment']

  def calc(self, services):
    elog = ELog()
    for i, v in self.m.items():
      s1 = services.getItem(v.get('service_from', ''))
      s2 = services.getItem(v.get('service_to', ''))
      if s1 is None:
        print("ERR: service '%s' not found " % v.get('service_from', ''))
        elog.log("LINK_ERROR", "ERR: service '%s' not found " % v.get('service_from', ''), v.get('service_from', ''), '')
        continue
      if s2 is None:
        print("ERR: service '%s' not found " % v.get('service_to', ''))
        elog.log("LINK_ERROR", "ERR: service '%s' not found " % v.get('service_to', ''), v.get('service_to', ''), '')
        continue
      if s1.get('domain', 's1') == s2.get('domain', 's2'):
        self.m[i]['domain'] = s1.get('domain', '')
