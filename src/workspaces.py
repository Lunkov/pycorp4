#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path

from urllib.parse import urlencode, quote
from pprint import pprint
from datetime import date

from .cfg import Cfg
from .workspace import Workspace

from .obj.tags import Tags
from .obj.systems import Systems
from .obj.data import DataSets
from .obj.nodes import Nodes
from .obj.links import Links
from .helpers.fs import FS
from .load.loader import Loader

import re


class Workspaces():
  def __init__ (self, fs: FS, config: Cfg, verbose = 0):
    self.__fs = fs
    self.__config = config
    self.__verbose = verbose
    
    self.__ws = {}

  def init(self):
    self.reload()

  def reload(self):
    wc = self.__config.getCfg('workspaces')
    loader = Loader(self.__verbose)
    for iw, wv in wc.items():
      if iw not in self.__ws:
        self.__ws[iw] = Workspace(iw, self.__fs, wv['path'], self.__verbose)
      self.__reload(loader, wv, self.__ws[iw])

  def reloadWorkspace(self, iw):
    cfg = self.__config.getCfg('workspaces')
    if (iw in self.__ws) and (iw in cfg):
      self.__ws[iw].clear()
      loader = Loader(self.__verbose)
      self.__reload(loader, cfg[iw], self.__ws[iw])

  def __reload(self, loader, cfg: dict, ws: Workspace):
    if 'loaddata' in cfg:
      if self.__verbose > 7:
        print('DBG: Load workspace: "%s"' % (ws.getName()))
      loader.run(ws, self.__fs.getPathData(), cfg['loaddata'])
  
  def getStat(self):
    return {}

  def getWorkspace(self, iw: str):
    if iw not in self.__ws:
      return {}
    return self.__ws[iw]
