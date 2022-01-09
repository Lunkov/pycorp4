#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import hashlib
import codecs
import yaml
from pathlib import Path

class Cfg():
  def __new__(self, verbose):
    if not hasattr(self, 'instance'):
      self.instance = super(Cfg, self).__new__(self)
      return self.instance

  def __init__ (self, verbose):
    super(Cfg, self).__init__()
    self.verbose = verbose
    self.cfg = {}

  def get(self):
    return self.cfg

  def getCfg(self, name):
    return self.cfg.get(name, {})

  def loadFromPath(self, pathname):
    fp = os.path.abspath(pathname)
    fullPath = fp
    if self.verbose:
      print("LOG: Config read from '%s'..." % fp)
    try:
      for path in Path(fp).rglob('*.cfg'):
        fullPath = os.path.join(fp, path.parent, path.name)
        if os.path.isfile(fullPath):
          self.load(fullPath)
          
    except Exception as err:
      print("FATAL: File(%s): %s" % (fullPath, str(err)))

  def load(self, fullPath):
    try:
      with codecs.open(fullPath, 'r', encoding='utf-8') as stream:
        config = yaml.safe_load(stream)
        self.cfg.update(config)
        if self.verbose:
          print("DBG: Config load %s" % fullPath)
    except yaml.YAMLError as exc:
      print("ERR: Bad format in %s: %s" % (fullPath, exc))
