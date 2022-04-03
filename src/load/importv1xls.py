#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys, traceback
import pylightxl as xl
from pprint import pprint
from .basicxls import BasicImportXLS
from src.workspace import Workspace
from src.obj.systems import System
from src.obj.links import Link
from src.obj.tags import Tag
from src.obj.data import DataSets, DataSet, DataFields, DataField

class ImportXLSV1(BasicImportXLS):

  def loadTopics(self, filename, workspace: Workspace):
    if (db := self.openFile(filename)) is None:
      return False

    nws = 'topics.links'
    if (sheet := self.openWorksheet(db, nws)) is None:
      return False
 
    try:
      columns, find = self.findColumns(sheet)
      
      ir = 0
      for row in sheet.rows:
        ir = ir + 1
        if ir == 1:
          continue
        tags = self.getValue(row, columns, 'tags', '')
        if (topic := self.getValue(row, columns, 'topic')) is None:
          continue
        if (sender := self.getValue(row, columns, 'sender')) is None:
          continue
        if (reciever := self.getValue(row, columns, 'reciever')) is None:
          continue
        workspace.getSystems().append(System().set({'id': sender,
                                                    'type': 'microservice',
                                                    'tags': tags}))
        workspace.getSystems().append(System().set({'id': reciever,
                                                    'type': 'microservice',
                                                    'tags': tags}))
        workspace.getSystems().append(System().set({'id': topic,
                                                    'type': 'kafka-topic',
                                                    'tags': tags}))
        
        workspace.getLinks().append(Link().set({'item_from': sender,
                                                'item_to': topic,
                                                'type': 'q-a-pub',
                                                'tags': tags}))

        workspace.getLinks().append(Link().set({'item_from': topic,
                                                'item_to': reciever,
                                                'type': 'q-a-sub',
                                                'tags': tags}))
        self.appendTags(workspace, tags)
                                                
    except Exception as err:
      print("ERR: readXLS(%s:%s): %s" % (filename, nws, str(err)))
      traceback.print_exc(file=sys.stdout)
      return False
    return True


  def loadData(self, filename, workspace: Workspace):
    if (db := self.openFile(filename)) is None:
      return False

    nws = 'data'
    if (sheet := self.openWorksheet(db, nws)) is not None:
      try:
        columns, find = self.findColumns(sheet)
        
        ir = 0
        for row in sheet.rows:
          ir = ir + 1
          if ir == 1:
            continue
          if (fid := self.getValue(row, columns, 'id')) is None:
            continue
          if (fname := self.getValue(row, columns, 'name')) is None:
            continue
          if (ftype := self.getValue(row, columns, 'type')) is None:
            continue
          workspace.getDataSets().append(DataSet().set({'id': fid,
                                                        'name': fname,
                                                        'type': ftype,
                                                        'tags': self.getValue(row, columns, 'type', ''),
                                                        'sizeof': self.getValue(row, columns, 'sizeof', 0)}))

      except Exception as err:
        print("ERR: readXLS(%s:%s): %s" % (filename, nws, str(err)))

    nws = 'data.fields'
    if (sheet := self.openWorksheet(db, nws)) is not None:
      try:
        columns, find = self.findColumns(sheet)
        ir = 0
        for row in sheet.rows:
          ir = ir + 1
          if ir == 1:
            continue
          if (parent := self.getValue(row, columns, 'parent')) is None:
            continue
          if (fname := self.getValue(row, columns, 'field')) is None:
            continue
          if (ftype := self.getValue(row, columns, 'type')) is None:
            continue
          if (flength := self.getValue(row, columns, 'length')) is None:
            continue
          workspace.getDataFields().append(DataField().set({'parent': parent,
                                                            'name':   fname,
                                                            'type':   ftype,
                                                            'length': flength}))
          
      except Exception as err:
        print("ERR: readXLS(%s:%s): %s" % (filename, 'data', str(err)))
        traceback.print_exc(file=sys.stdout)

    return True

  def loadDB(self, filename, workspace: Workspace):
    if (db := self.openFile(filename)) is None:
      return False
      
    nws = 'db.info'
    if (sheet := self.openWorksheet(db, nws)) is not None:
      try:
        columns, find = self.findColumns(sheet)
        
        ir = 0
        for row in sheet.rows:
          ir = ir + 1
          if ir == 1:
            continue
          if (fname := self.getValue(row, columns, 'db.table.name')) is None:
            continue
          if (fdescription := self.getValue(row, columns, 'db.table.description')) is None:
            continue
          tags = self.getValue(row, columns, 'tags', '')
          dbname = self.getValue(row, columns, 'db.name')
          ftname = dbname + '.' + fname
          workspace.getDataSets().append(DataSet().set({'id': ftname,
                                                        'name': fname,
                                                        'description': fdescription}))
          workspace.getSystems().append(System().set({'id': dbname,
                                                        'type': 'db',
                                                        'tags': tags}))
          
          workspace.getLinks().append(Link().set({'item_from': dbname,
                                                  'item_to': ftname,
                                                  'type': 'table',
                                                  'tags': tags}))
          self.appendTags(workspace, tags)

      except Exception as err:
        print("ERR: readXLS(%s:%s): %s" % (filename, nws, str(err)))
        
    nws = 'db.system'
    if (sheet := self.openWorksheet(db, nws)) is not None:
      try:
        columns, find = self.findColumns(sheet)
        
        ir = 0
        for row in sheet.rows:
          ir = ir + 1
          if ir == 1:
            continue
          tags = self.getValue(row, columns, 'tags', '')
          if (sname := self.getValue(row, columns, 'system.name')) is not None:
            workspace.getSystems().append(System().set({'id': sname,
                                                        'type': 'system',
                                                        'tags': tags}))

          if (dbname := self.getValue(row, columns, 'db.name')) is not None:
            workspace.getSystems().append(System().set({'id': dbname,
                                                        'type': 'db',
                                                        'tags': tags}))
          
          workspace.getLinks().append(Link().set({'item_from': sname,
                                                  'item_to': dbname,
                                                  'type': 'db',
                                                  'tags': tags}))
          self.appendTags(workspace, tags)

      except Exception as err:
        print("ERR: readXLS(%s:%s): %s" % (filename, nws, str(err)))

    nws = 'db.tables'
    if (sheet := self.openWorksheet(db, nws)) is not None:
      try:
        columns, find = self.findColumns(sheet)
        
        ir = 0
        for row in sheet.rows:
          ir = ir + 1
          if ir == 1:
            continue
          dbname = self.getValue(row, columns, 'db.name')
          fname = self.getValue(row, columns, 'table.name')
          ftname = dbname + '.' + fname
          if (fname := self.getValue(row, columns, 'table.field.name')) is None:
            continue
          ftype = self.getValue(row, columns, 'table.field.type', 'undefined')
          flength = self.getValue(row, columns, 'table.field.length', 0)
          workspace.getDataFields().append(DataField().set({'parent': ftname,
                                                            'name':   fname,
                                                            'type':   ftype,
                                                            'length': flength}))
          

      except Exception as err:
        print("ERR: readXLS(%s:%s): %s" % (filename, nws, str(err)))
    return True

  def appendTags(self, workspace, tags):
    t = tags.split(',')
    for it in t:
      workspace.getTags().append(Tag().set({'id': it}))
