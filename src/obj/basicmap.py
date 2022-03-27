#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import codecs
import json
import hashlib
import pylightxl as xl
import numpy as np
from pathlib import Path
from pprint import pprint

from .basic import Basic

class BasicMap():
  def __init__ (self, fields, f_index, i):
    self.__i = i
    self.__fields = fields
    self.__f_index = f_index
    self.__data = {}
    self.__index = {}

  def setIndex(self, mapI):
    self.__index = mapI

  def count(self):
    return len(self.__data)

  def clone(self):
    c = self.__class__()
    c.setIndex(self.__index)
    c.__i = self.__i
    c.__fields = self.__fields
    c.__f_index = self.__f_index
    return c
  
  def append(self, item):
    if item.getId() == '':
      return
    if item.getId() in self.__data:
      self.__data[item.getId()].update(item.get())
    else:
      self.__data[item.getId()] = item.get()
  
  def getItem(self, name):
    if name in self.__data:
      return self.__data[name]
    return None

  def appendData(self, data: dict):
    self.__data.update(data)

  def get(self):
    return self.__data

  def getVariants(self, field):
    res = {}
    for key, value in self.__data.items():
      if type(value[field]) is list:
        for v in value[field]:
          res[v] = 1
      else:
        res[value[field]] = 1
    return list(res.keys())

  def makeIndexes(self):
    for i in self.__f_index:
      self.makeIndex(i)
    
  def makeIndex(self, field):
    self.__index[field] = {}
    for key, item in self.__data.items():
      if not field in item:
        if not 'NONE' in self.__index[field]:
          self.__index[field]['NONE'] = []
        self.__index[field]['NONE'].append(key)
        continue
      if type(item[field]) is list:  
        for item in item[field]:
          if not item in self.__index[field]:
            self.__index[field][item] = []
          self.__index[field][item].append(key)
      else:
        if not item[field] in self.__index[field]:
          self.__index[field][item[field]] = []
        self.__index[field][item[field]].append(key)
    
  def filter(self, field, val):
    if not field in self.__index:
      self.makeIndex(field)
    
    res = self.clone()
    if type(val) is list:
      if 'all' in val:
        return self
      
      for key in val:
        if key in self.__index[field]:
          for ki in self.__index[field][key]:
            res.append(self.__i.set(self.getItem(ki)))
    else:
      if type(val) is dict:
        pprint(val)
      else:
        if field in self.__index:
          if val in self.__index[field]:
            for ki in self.__index[field][val]:
              res.append(self.__i.set(self.getItem(ki)))
    return res

  def getName(self):
    return self.__class__.__name__
