#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
    if self.verbose:
      print("LOG: Swaggers: Scaning folder '%s'..." % swaggerpath)
    lstDir = ''
    try:
      lstDir = os.listdir(swaggerpath)
    except:
      print("FATAL: Folder Not Found: %s" % (swaggerpath))

    sw = Swagger()
    for curDir in lstDir:
      if self.verbose:
        print("DBG: scan subfolder: %s" % curDir)
      fullPath = os.path.join(swaggerpath, curDir)
      if os.path.isdir(fullPath):
        sw.load(os.path.join(fullPath, '.yaml'))

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

