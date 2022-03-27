#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path
import pylightxl as xl

from urllib.parse import urlencode, quote
from pprint import pprint
from datetime import date

from .obj.business_domains import BusinessDomains
from .obj.tags import Tags
from .obj.services import Services
from .obj.nodes import Nodes
from .obj.links import Links
from .obj.solutions import Solutions
from .helpers.fs import FS

import re


class Workspaces():
  def __init__ (self, fs, config, verbose):
    self._fs = fs
    self._config = config
    self._verbose = verbose
    
    self._ws = {}

  def init():
    ws = self.config.getCfg('workspaces')
    for iw, wv in ws.items():
      self._ws[iw] = Workspace(iw, self.__fs, wv, self.__verbose)

  def reload(self, iw):
    w = self._config.getCfg('workspaces')
    if iw in self._ws:
      self._ws[iw].load()

  def loadAll(self):
    ws = self._config.getCfg('workspaces')
    for iw, wv in ws.items():
      if iw in self._ws:
        self._ws[iw].load()

