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
    self.fields = ['id', 'name', 'title', 'domain', 'type', 'status', 'layer', 'tags', 'description', 'link', 'git', 'version', 'swagger', 'swagger_date', 'swagger_status', 'max_rps', 'max_rps_high', 'rt_99', 'rt_95', '5xx']

  def graph(self, D, service):
    D.node(service.get('id', 'xz'),
           service.get('name', 'xz'),
           service.get('domain', 'undef'), 
           service.get('type', 'service'),
           service.get('status', 'undef'),
           service.get('link', ''),
           service.get('description', ''))

