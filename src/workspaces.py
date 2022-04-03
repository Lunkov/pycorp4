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
    ws = self.__config.getCfg('workspaces')
    for iw, wv in ws.items():
      self.__ws[iw] = Workspace(iw, self.__fs, wv['path'], self.__verbose)

  def reload(self):
    wc = self.__config.getCfg('workspaces')
    loader = Loader()
    for iw, wv in wc.items():
      if iw in self.__ws:
        if 'loaddata' in wv:
          loader.run(self.__ws[iw], self.__fs.getPathData(), wv['loaddata'])
  
  def getStat(self):
    return {}

  def getWorkspace(self, iw: str):
    if iw not in self.__ws:
      return {}
    return self.__ws[iw]
