#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import codecs
import json
import hashlib
import pylightxl as xl
import numpy as np
from pprint import pprint

class Basic():
  def __init__ (self):
    self.name = 'unknown'
    self.m = {}
    self.dia = {}
    self.ids = []
    self.fields = []
  
  def updateItem(self, name, properties):
    if name in self.m:
      prop = self.m[name]
      properties.update(self.normProp(prop))

    self.addItem(name, properties)

  def normProp(self, properties):
    for c in self.fields:
      if not c in properties:
        properties[c] = ''

    if ('tags' in properties) and (type(properties['tags']) is str):
      properties['tags'] = np.array(properties['tags'].split(',')).tolist()
      properties['tags'] = list(filter(None, properties['tags']))
    return properties

  def addItem(self, name, properties):
    if name == '':
      return
    self.dia[name] = None
    self.m[name] = self.normProp(properties)
  
  def getItem(self, name):
    if name in self.m:
      return self.m[name]
    return None

  def set(self, mapV):
    self.m = mapV
    
  def append(self, mapV):
    self.m.update(mapV)

  def get(self):
    return self.m

  def getItems(self):
    return self.m.items()

  def getVariants(self, field):
    res = {}
    for key, value in self.m.items():
      if type(value[field]) is list:
        for v in value[field]:
          res[v] = 1
      else:
        res[value[field]] = 1
    return list(res.keys())

  def filter(self, field, val):
    res = {}
    for key, value in self.m.items():
      if not field in value:
        continue
      if type(val) is list:
        if len(val) < 1:
          continue
        if 'all' in val:
          res[key] = value
          continue
        if type(value[field]) is list:
          if len(value[field]) < 1:
            continue
          if 'all' in value[field]:
            res[key] = value
            continue
          for item in value[field]:
            if item in val:
              res[key] = value
              break
        else:
          if value[field] == '':
            continue
          if 'all' == value[field]:
            res[key] = value
            continue
          if value[field] in val:
            res[key] = value
      else:
        if val == '':
          continue
        if 'all' == val:
          res[key] = value
          continue
        if type(value[field]) is list:
          if len(value[field]) < 1:
            continue
          if 'all' in value[field]:
            res[key] = value
            continue
          if val in value[field]:
            res[key] = value
        else:
          if value[field] == '':
            continue
          if 'all' == value[field]:
            res[key] = value
            continue
          if value[field].find(val) > -1:
            res[key] = value
    return res

  def getCount(self):
    return len(self.m)

  def getName(self):
    return self.name

  def dumpCSV(self, filename):
    text_file = codecs.open(filename, 'w', 'utf-8')
    text_file.write("%s\n" % ','.join(self.fields))
    
    for i, v in self.m.items():
      rec = i + ','
      for c in self.fields:
        rec = rec + '\"' + v[c] + '\"' + ','
      rec = rec + "\n"
      text_file.write(rec)      

    text_file.close()  

  def findColumns(self, xls, worksheet):
    columns = {}
    find = False
    pos = 1
    for i, row in enumerate(xls.ws(ws = worksheet).rows, start=pos):
      if find:
        break
      for j, col in enumerate(row):
        if col != '':
          # sj = str(j)
          if col in self.fields:
            columns[col] = j
            find = True
          else:
            columns[col] = j
            find = True
    return columns, find
    
  def readXLS(self, xls, worksheet):
    columns, ok = self.findColumns(xls, worksheet)
    if not ok:
      print("ERR: Read titles %s" % worksheet)
      return
    for i, row in enumerate(xls.ws(ws = worksheet).rows, start=1):
      if i == 1:
        continue
      value = {}
      key  = ''
      for c in self.fields:
        if not c in columns:
          continue
        value[c] = str(row[columns[c]]).strip()
        if c == 'id':
          key = value[c]
      if key == '' and len(self.ids) > 0:
        key = self.genId(value)
      if key != '':
        self.addItem(key, value)
      else:
        print("ERR: id not set for %s" % worksheet)

  def genId(self, properties):
    key = ''
    for j in self.ids:
      key = key + '*' + properties.get(j, '')
    return hashlib.md5(key.encode('utf-8')).hexdigest()

  def genCode(self, properties):
    key = ''
    for j in self.ids:
      key = key + '.' + properties.get(j, '')
    return key

  def writeXLS(self, xls, worksheet):
    columns = {}
    xls.add_ws(ws = worksheet)
    irow = 1
    for j, c in enumerate(self.fields):
      xls.ws(ws = worksheet).update_index(row = irow, col = j + 1, val = c)
      columns[j] = c

    irow = 2
    for key, value in self.m.items():
      for j, c in enumerate(self.fields):
        xls.ws(ws = worksheet).update_index(row = irow, col = j + 1, val = value[columns[j]])
      irow = irow + 1

  def writeJSON(self, filename):
    with codecs.open(filename, 'w', 'utf-8') as outfile:
      json.dump(self.m, outfile)

  def readJSON(self, filename):
    if os.path.isfile(filename):
      with codecs.open(filename, 'r', 'utf-8') as infile:
        self.m = json.load(infile)
