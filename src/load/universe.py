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
    self.__id = 'unknown'

  def openFile(self, filename):
    db = None
    try:
      fn = os.path.realpath(filename)
      db = xl.readxl(fn = fn)

    except Exception as err:
      print("ERR: XLS.Open(%s): %s" % (fn, str(err)))
      return None
    return db

  def openWorksheet(self, db, worksheet):
    sheet = None
    try:
      sheet = db.ws(ws = worksheet)

    except Exception as err:
      print("ERR: XLS.WS(%s): %s" % (worksheet, str(err)))
      return None
    return sheet

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

  def getValue(self, row, columns, name, default = None):
    if name in columns:
      if columns[name] < len(row):
        return row[columns[name]]
    return default
