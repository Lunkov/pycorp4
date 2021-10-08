#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic
    
class Services(Basic):
  def __init__ (self):
    super(Services, self).__init__()
    self.name = 'services'
    self.fields = ['id', 'name', 'title', 'domain', 'type', 'status', 'layer', 'tags', 'description', 'link', 'git', 'version', 'swagger', 'swagger_date', 'swagger_status', 'max_rps', 'max_rps_high', 'rt_99', 'rt_95', '5xx']


