#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path
import pylightxl as xl

from urllib.parse import urlencode, quote
from pprint import pprint
from datetime import date

from .obj.tags import Tags
from .obj.systems import Systems
from .obj.nodes import Nodes
from .obj.links import Links
from .obj.interfaces import Interfaces
from .obj.data import DataSets, DataFields
from .helpers.fs import FS

import re


class Workspace():
  def __init__ (self, name, fs: FS, verbose = 0):
    self.__name = name
    
    self.__fs = fs
    self.__verbose = verbose

    self.__systems = Systems()
    self.__interfaces = Interfaces()
    self.__links = Links()

    self.__nodes = Nodes()
    
    self.__tags = Tags()
    
    self.__dataSets = DataSets()
    self.__dataFields = DataFields()
  
  def getSystems(self):
    return self.__systems

  def getLinks(self):
    return self.__links

  def getInterfaces(self):
    return self.__intefaces

  def getNodes(self):
    return self.__nodes

  def getNetworks(self):
    return self.__networks

  def getDataSets(self):
    return self.__dataSets

  def getDataFields(self):
    return self.__dataFields
