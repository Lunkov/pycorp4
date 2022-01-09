#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
from .basic import Basic

class Singleton(type):
  _instances = {}
  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    return cls._instances[cls]
        
class ELog(Basic, metaclass=Singleton):
  
  def __init__ (self):
    super(ELog, self).__init__()
    self.name = 'elog'
    self.fields = ['msgtype', 'description', 'service', 'link']


  def log(self, msgtype, description, service, link):
    idn = hashlib.md5((msgtype+description+service).encode('utf-8')).hexdigest()
    self.addItem(idn, {'msgtype': msgtype, 'description': description, 'service': service, 'link': link})
