#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic
from .swagger import Swagger
from .elog import ELog

import hashlib
import re

from diagrams.gcp.compute import Functions
from diagrams.aws.integration import SQS
from diagrams.aws.network import ELB
from diagrams.aws.database import RDS

class Service():
  def __init__ (self):
    self.v = {}
    
  def get(self, name):
    return self.v.get(name, '')

  def set(self, v):
    self.v = v
    
class Services(Basic):
  def __init__ (self):
    super(Services, self).__init__()
    self.name = 'services'
    self.fields = ['id', 'name', 'title', 'domain', 'type', 'status', 'layer', 'tags', 'description', 'link', 'git', 'version', 'swagger', 'swagger_date', 'swagger_status']

  def updateSwaggerAll(self, dt):
    sw = Swagger()
    for key, service in self.m.items():
      ok = self.updateSwagger(service, sw)
      if ok:
        self.m[key]['version'] = sw.getVersion()
        self.m[key]['swagger_status'] = 'ok'
        self.m[key]['swagger_date'] = dt
        sw.save(dt)
    
  def graphWULF(self, G):
    for i, v in self.m.items():
      G.add_node(i)
      G.add_edge(i, v['domain'])
    for n, data in G.nodes(data=True):
      if n in self.m:
        data['size'] = 0.5

  def graphVIZ(self, G):
    for i, v in self.m.items():
      G.add_node(i, label = i, color = '#005f02', size = 10, shape = 'diamond', group = v['domain'])      
      G.add_edge(i, v['domain'])

  def graph(self, D, service):
    D.node(service.get('id', 'xz'),
           service.get('name', 'xz'),
           service.get('domain', 'undef'), 
           service.get('type', 'service'),
           service.get('status', 'undef'),
           service.get('link', ''),
           service.get('description', ''))

