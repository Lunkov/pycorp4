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
  def __init__ (self, fields, ids, splitfields, typeid = 'code'):
    self.__fields = fields
    self.__ids = ids
    self.__splitfields = splitfields
    self.__typeid = typeid
    self.__strSeparator = ','

    self.__id = ''
    self.__uid = ''
    self.__code = ''
    self.__name = ''
    self.__data = {}

  def set(self, properties: dict):
    self.__data = self.__normProp(properties)
    self.__uid = self.genUID()
    self.__code = self.genCode()
    if self.__typeid == 'code':
      self.__id = self.__data.get('id', self.__code)
    else:
      self.__id = self.__data.get('id', self.__uid)
    if not 'id' in self.__data:
      self.__data['id'] = self.__id
    if not 'code' in self.__data:
      self.__data['code'] = self.__code
    if not 'name' in self.__data:
      self.__data['name'] = self.__id
    self.__name = self.__data.get('name', 'undef')
    return self

  def get(self):
    return self.__data

  def getId(self):
    return str(self.__id)

  def getUID(self):
    return str(self.__uid)

  def getCode(self):
    return str(self.__code)

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

  def genUID(self):
    key = ''
    for j in self.__ids:
      key = str(key) + '*' + str(self.__data.get(j, ''))
    return hashlib.md5(key.encode('utf-8')).hexdigest()

  def genCode(self):
    key = ''
    for j in self.__ids:
      if key == '':
        key = self.__data.get(j, '')
        continue
      key = str(key) + '.' + str(self.__data.get(j, ''))
    return key

  def calcStorageSize(self, duration):
    return 0
