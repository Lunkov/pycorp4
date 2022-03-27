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

class BasicImportXLS():
  def __init__ (self):
    self.id = 'unknown'

  def findColumns(self, worksheet):
    columns = {}
    find = False
    pos = 1
    for i, row in enumerate(worksheet.rows, start=pos):
      if find:
        break
      for j, col in enumerate(row):
        if col != '':
          columns[col] = j
          find = True
    return columns, find
'''    
  def readXLSentity(self, xls, worksheet, entity):
    try:
      columns, ok = self._findColumns(xls, worksheet)
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
        entity.addItem(key, value)

    except Exception as err:
      print("ERR: readXLS(ws:%s): %s" % (worksheet, str(err)))

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

  def loadYAMLFromPath(self, pathname, mask, verbose):
    fp = os.path.abspath(pathname)
    fullPath = fp
    if verbose > 8:
      print("LOG: Config read from '%s'..." % fp)
    try:
      for path in Path(fp).rglob(mask):
        fullPath = os.path.join(fp, path.parent, path.name)
        if os.path.isfile(fullPath):
          self.loadYAML(fullPath, verbose)
          
    except Exception as err:
      print("FATAL: File(%s): %s" % (fullPath, str(err)))

  def loadYAML(self, fullPath, verbose):
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
'''
