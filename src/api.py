#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
from .basic import Basic

class API(Basic):
  def __init__ (self):
    super(API, self).__init__()
    self.name = 'api'
    self.ids = ['service', 'version', 'api', 'method']
    self.fields = ['id', 'code', 'name', 'title', 'service', 'method', 'api', 'version', 'status', 'description', 'link', 'linkin']

  def addItem(self, name, properties):
    properties['code'] = self.genCode(properties)
    properties['linkin'] = hashlib.md5(("%s.%s.%s" % (properties.get('service', ''), properties.get('method', ''), properties.get('api', ''))).encode('utf-8')).hexdigest()
    super(API, self).addItem(name, properties)
