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
  def __init__ (self, name, fs: FS, path: str, verbose = 0):
    self.__name = name
    
    self.__fs = fs
    self.__path = path
    self.__verbose = verbose

    self.__systems = Systems()
    self.__interfaces = Interfaces()
    self.__links = Links()

    self.__nodes = Nodes()
    
    self.__tags = Tags()
    
    self.__dataSets = DataSets()
    self.__dataFields = DataFields()
    
    if self.__verbose > 7:
      print("DBG: Init workspace '%s'" % name)
  
  def getSystems(self):
    return self.__systems

  def getLinks(self):
    return self.__links

  def getTags(self):
    return self.__tags

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
  
  def getPath(self):
    return self.__path

  def getStat(self):
    return {'path': self.__path,
            'cnt_tags': self.__tags.count(),
            'cnt_systems': self.__systems.count(),
            'cnt_links': self.__links.count()
           }

  def filterSystem(self, systemname):
    systems = self.__systems.filter('id', systemname)
    
    flinks = self.__links.filter('item_from', systemname)
    linksTo = self.__links.filter('item_to', systemname)
    flinks.appendData(linksTo.get().items())
    
    srvsTo = flinks.getVariants('item_to')
    srvs1 = self.__systems.filter('id', srvsTo)
    systems.appendData(srvs1.get().items())
    
    srvsFrom = flinks.getVariants('item_from')
    srvs1 = self.__systems.filter('id', srvsFrom)
    systems.appendData(srvs1.get().items())

    return systems, flinks

  def filterTag(self, tagname):

    flinks = Links()
    systems = self.__systems.filter('tags', tagname)
    
    lsrv = systems.getVariants('id')
    
    links = self.__links.filter('tags', tagname)
    flinks.appendData(links.get().items())

    srvsTo = flinks.getVariants('item_to')
    srvs1 = self.__systems.filter('id', srvsTo)
    systems.appendData(srvs1.get().items())
    
    srvsFrom = flinks.getVariants('item_from')
    srvs1 = self.__systems.filter('id', srvsFrom)
    systems.appendData(srvs1.get().items())

    return systems, flinks
