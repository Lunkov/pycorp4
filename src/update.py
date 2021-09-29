#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .basic import Basic

class Updates(Basic):
  def __init__ (self, verbose):
    super(Updates, self).__init__()
    self.m = {}
    self.name = 'update'
    self.ids = ['id', 'name', 'service', 'version']
    self.fields = ['id', 'name', 'service', 'plan', 'version', 'sequence', 'swagger']
    self.verbose = verbose

  def load(self, updatepath):
    if self.verbose:
      print("LOG: Updates: Scaning folder '%s'..." % updatepath)
    lstDir = ''
    try:
      lstDir = os.listdir(updatepath)
    except:
      print("FATAL: Folder Not Found: %s" % (updatepath))

    for curDir in lstDir:
      if self.verbose:
        print("DBG: scan subfolder: %s" % curDir)
      fullPath = os.path.join(updatepath, curDir)
      if os.path.isdir(fullPath):
        with open(os.path.join(fullPath, ".yaml"), 'r') as stream:
          try:
            prop = yaml.safe_load(stream)
            key = self.genId(prop)
            if key != '':
              self.addItem(key, prop)

          except yaml.YAMLError as exc:
            print("ERR: Bad format in %s: %s" % (fullPath, exc))    
