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

'''
 Basic class for entities
'''
class Basic():
  def __init__ (self, fields, ids, splitfields):
    self.__fields = fields
    self.__ids = ids
    self.__splitfields = splitfields
    self.__strSeparator = ','

    self.__id = ''
    self.__uid = ''
    self.__code = ''
    self.__name = ''
    self.__data = {}

  def set(self, properties: dict):
    self.__data = self.__normProp(properties)
    self.__id = self.__data.get('id', self.__genUID())
    self.__uid = self.__genUID()
    self.__code = self.__genCode(self.__data)
    self.__name = self.__data.get('name', 'undef')
    return self

  def get(self):
    return self.__data

  def getId(self):
    return self.__id

  def getUID(self):
    return self.__uid

  def getCode(self):
    return self.__code

  def getName(self):
    return self.__name

  def getFields(self):
    return self.__fields

  def __normProp(self, properties: dict):
    for c in self.__fields:
      if c in self.__splitfields:
        if not c in properties:
          properties[c] = []
        else:
          if (type(properties[c]) is str):
            tmp = np.array(properties[c].split(self.__strSeparator)).tolist()
            properties[c] = list(filter(None, tmp))
    return properties

  def __genUID(self):
    key = ''
    for j in self.__ids:
      key = key + '*' + self.__data.get(j, '')
    return hashlib.md5(key.encode('utf-8')).hexdigest()

  def __genCode(self, properties):
    key = ''
    for j in self.__ids:
      key = key + '.' + properties.get(j, '')
    return key

  def calcStorageSize(self, duration):
    return 0
