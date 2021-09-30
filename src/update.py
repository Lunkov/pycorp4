#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import yaml
from pathlib import Path
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
    fp = os.path.abspath(updatepath)
    if self.verbose:
      print("LOG: Updates: Scaning folder '%s'..." % fp)
    try:

      for path in Path(fp).rglob('*.yaml'):
        fullPath = os.path.join(fp, path.name)
        if not os.path.isdir(fullPath):
          if self.verbose:
            print("DBG: Scan: %s" % fullPath)
          with open(fullPath, 'r') as stream:
            try:
              prop = yaml.safe_load(stream)
              key = self.genId(prop)
              if key != '':
                self.addItem(key, prop)

            except yaml.YAMLError as err:
              print("ERR: Bad format in %s: %s" % (fullPath, str(err)))    

    except Exception as err:
      print("FATAL: Folder Not Found: %s: %s" % (fp, str(err)))
