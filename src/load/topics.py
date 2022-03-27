#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys, traceback
import pylightxl as xl
from .basicxls import BasicImportXLS
from src.workspace import Workspace
from src.obj.systems import System
from src.obj.links import Link

class ImportXLS(BasicImportXLS):
  
  def loadTopics(self, filename, workspace: Workspace):
    try:
      fn = os.path.realpath(filename)
      db = xl.readxl(fn = fn)
      sheet = db.ws(ws='topics')
      
      columns, find = self.findColumns(sheet)
      
      ir = 0
      for row in sheet.rows:
        ir = ir + 1
        if ir == 1:
          continue
        workspace.getSystems().append(System().set({'id': row[columns['sender']],   'type': 'microservice', 'tags': row[columns['tags']]}))
        workspace.getSystems().append(System().set({'id': row[columns['reciever']], 'type': 'microservice', 'tags': row[columns['tags']]}))
        workspace.getSystems().append(System().set({'id': row[columns['topic']],    'type': 'kafka-topic',  'tags': row[columns['tags']]}))
        
        workspace.getLinks().append(Link().set({'item_from': row[columns['sender']],
                                                'item_to': row[columns['topic']],
                                                'type': 'q-a-pub',
                                                'tags': row[columns['tags']]}))

        workspace.getLinks().append(Link().set({'item_from': row[columns['topic']],
                                                'item_to': row[columns['reciever']],
                                                'type': 'q-a-sub',
                                                'tags': row[columns['tags']]}))

    except Exception as err:
      print("ERR: readXLS(%s:%s): %s" % (fn, 'topics', str(err)))
      traceback.print_exc(file=sys.stdout)
      return False
    return True
