#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import codecs
import json
import hashlib
import glob
import pylightxl as xl
import numpy as np
from pathlib import Path
from pprint import pprint

from src.load.importv1xls import ImportXLSV1
from src.workspace import Workspace

class Loader():
  def __init__ (self, verbose):
    self.__verbose = verbose

  def run(self, workspace: Workspace, pathname, loadmap):
    for i in list(loadmap):
      if 'engine' not in i:
        continue
      engine = i['engine']
      if 'pathmask' in i:
        fullPath = os.path.join(os.path.abspath(pathname), workspace.getPath())
        try:
          files = [f for f in glob.glob(os.path.join(fullPath, i['pathmask']), recursive=True)]
          for path in files:
            if os.path.isfile(path):
              self.loadEngine(engine, path, workspace)
              
        except Exception as err:
          print("FATAL: File(%s): %s" % (fullPath, str(err)))
  
  def loadEngine(self, engine, fullPath, workspace: Workspace):
    c = engine.split('.')
    if self.__verbose > 7:
      print('DBG: Load by engine: %s("%s")' % (engine, fullPath))
    if len(c) < 2:
      return False
    ok = False
    if c[0] == 'ImportXLSV1':
      ix = ImportXLSV1()
      method = getattr(ix, c[1])
      if method is not None:
        ok = method(fullPath, workspace)
    return ok
