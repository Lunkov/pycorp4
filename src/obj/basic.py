#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import codecs
import json
import hashlib
import pylightxl as xl
import numpy as np
from pathlib import Path

class Basic():
  def __init__ (self):
    self.name = 'unknown'
    self.data = {}
    self.fields = []
    self.ids = []
    self.index = {}
    self.f_index = []
    self.dia = {}

  def setData(self, mapV):
    self.data = mapV

  def getData(self):
    return self.data

  def setIndex(self, mapI):
    self.index = mapI

  def getCount(self):
    return len(self.data)

  def clone(self):
    c = self.__class__()
    c.setIndex(self.index)
    return c
  
  def updateItem(self, name, properties):
    if name in self.data:
      prop = self.data[name]
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
    self.data[name] = self.normProp(properties)
  
  def getItem(self, name):
    if name in self.data:
      return self.data[name]
    return None

  def append(self, m):
    self.data.update(m.getData())

  def appendData(self, mapV):
    self.data.update(mapV)

  def getItems(self):
    return self.data.items()

  def getVariants(self, field):
    res = {}
    for key, value in self.data.items():
      if type(value[field]) is list:
        for v in value[field]:
          res[v] = 1
      else:
        res[value[field]] = 1
    return list(res.keys())

  def makeIndexes(self):
    for i in self.f_index:
      self.makeIndex(i)
    
  def makeIndex(self, field):
    self.index[field] = {}
    for key, value in self.data.items():
      if not field in value:
        if not 'NONE' in self.index[field]:
          self.index[field]['NONE'] = []
        self.index[field]['NONE'].append(key)
        continue
      if type(value[field]) is list:  
        for item in value[field]:
          if not item in self.index[field]:
            self.index[field][item] = []
          self.index[field][item].append(key)
      else:
        if not value[field] in self.index[field]:
          self.index[field][value[field]] = []
        self.index[field][value[field]].append(key)
    
  def filter(self, field, val):
    if not field in self.index:
      self.makeIndex(field)
    
    res = self.clone()
    if type(val) is list:
      if 'all' in val:
        return self
      
      for key in val:
        if key in self.index[field]:
          for ki in self.index[field][key]:
            res.addItem(ki, self.data[ki])
    else:
      if val in self.index[field]:
        for ki in self.index[field][val]:
          res.addItem(ki, self.data[ki])
    return res

  def getName(self):
    return self.name

  def dumpCSV(self, filename):
    text_file = codecs.open(filename, 'w', 'utf-8')
    text_file.write("%s\n" % ','.join(self.fields))
    
    for i, v in self.data.items():
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
    try:
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
    except Exception as err:
      print("ERR: readXLS(ws:%s): %s" % (worksheet, str(err)))

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
    for key, value in self.data.items():
      for j, c in enumerate(self.fields):
        xls.ws(ws = worksheet).update_index(row = irow, col = j + 1, val = value[columns[j]])
      irow = irow + 1

  def writeJSON(self, filename):
    try:
      with codecs.open(filename, 'w', 'utf-8') as outfile:
        json.dump(self.data, outfile, default=str)
    except Exception as err:
      print("FATAL: writeJSON(%s): %s" % (filename, str(err)))

  def readJSON(self, filename):
    try:
      if os.path.isfile(filename):
        with codecs.open(filename, 'r', 'utf-8') as infile:
          self.data = json.load(infile)
    except Exception as err:
      print("FATAL: readJSON(%s): %s" % (filename, str(err)))

  def loadFromPath(self, pathname, mask, verbose):
    fp = os.path.abspath(pathname)
    fullPath = fp
    if verbose > 8:
      print("LOG: Config read from '%s'..." % fp)
    try:
      for path in Path(fp).rglob(mask):
        fullPath = os.path.join(fp, path.parent, path.name)
        if os.path.isfile(fullPath):
          self.load(fullPath, verbose)
          
    except Exception as err:
      print("FATAL: File(%s): %s" % (fullPath, str(err)))

  def load(self, fullPath, verbose):
    try:
      with codecs.open(fullPath, 'r', encoding='utf-8') as stream:
        item = yaml.safe_load(stream)
        if 'code' in item:
          if item['code'] in self.data:
            self.data[item['code']].update(item)
          else:
            self.data[item['code']] = item
        if verbose > 2:
          print("DBG: Item load %s" % fullPath)
    except yaml.YAMLError as exc:
      print("ERR: Bad format in %s: %s" % (fullPath, exc))
