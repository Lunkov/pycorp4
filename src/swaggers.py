#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import yaml
from pathlib import Path
from .basic import Basic
from .swagger import Swagger

class Swaggers(Basic):
  def __init__ (self, verbose):
    super(Swaggers, self).__init__()
    self.m = {}
    self.name = 'swaggers'
    self.ids = ['service', 'version']
    self.fields = ['id', 'service', 'plan', 'fact', 'version', 'swagger-data']
    self.verbose = verbose

  def load(self, swaggerpath):
    fp = os.path.abspath(swaggerpath)
    if self.verbose:
      print("LOG: Swaggers: Scaning folder '%s'..." % fp)
    try:
      sw = Swagger()
      for path in Path(fp).rglob('*.yaml'):
        fullPath = os.path.join(fp, path.name)
        if not os.path.isdir(fullPath):
          sw.load(fullPath)

          prop = {}
          prop['version'] = sw.getVersion()
          prop['service'] = sw.getName()
          prop['swagger-data'] = sw.get()
          prop['plan'] = False
          prop['fact'] = True
          key = self.genId(prop)
          prop['id'] = key
          
          if key != '':
            self.addItem(key, prop)

    except Exception as err:
      print("FATAL: Folder Not Found: %s: %s" % (fp, str(err)))
