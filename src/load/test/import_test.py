#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import sys
import os
from pprint import pprint
from src.load.importv1xls import ImportXLSV1
from src.workspace import Workspace

class TestImportData(unittest.TestCase):

  def testTopics(self):

    w = Workspace('test', None, '', 0)
    ix = ImportXLSV1()
    ok = ix.loadTopics('src/load/test/data/Topics.xlsx', w)
    
    self.assertEqual(ok, True)
    self.assertEqual(w.getSystems().count(), 27)
    self.assertEqual(w.getSystems().getItem('Service 1'), {'id': 'Service 1', 'layers': [], 'tags': ['tag1']})
    self.assertEqual(w.getLinks().count(), 32)
    self.assertEqual(w.getLinks().getItem('27648c0f118c43ef73bb5b03815c61ee'), {'link_from': 'Service 1', 'link_to': 'Topic 1', 'type': 'data', 'tags': 'tag1'})

  def testData(self):

    w = Workspace('test', None, '', 0)
    ix = ImportXLSV1()
    ok = ix.loadData('src/load/test/data/DB.xlsx', w)
    
    self.assertEqual(ok, True)
    self.assertEqual(w.getDataSets().count(), 5)
    self.assertEqual(w.getDataFields().count(), 6)
    self.assertEqual(w.getDataSets().getItem('data2'), {'id': 'data2', 'name': 'data name 2', 'sizeof': 30, 'tags': [], 'type': ''})
    self.assertEqual(w.getDataFields().getItem('data2.field7'), {'parent': 'data2', 'name': 'field7', 'type': 'string', 'length': 10, 'sizeof': 22, 'tags': []})

  def testDB(self):

    w = Workspace('test', None, '', 0)
    ix = ImportXLSV1()
    ok = ix.loadDB('src/load/test/data/DB.xlsx', w)
    
    self.assertEqual(ok, True)
    self.assertEqual(w.getDataSets().count(), 3)
    self.assertEqual(w.getSystems().count(), 8)
    self.assertEqual(w.getDataFields().count(), 4)
    self.assertEqual(w.getDataSets().getItem('db1.table1'), {'id': 'db1.table1', 'name': 'table1', 'description': '', 'tags': []})
    self.assertEqual(w.getDataFields().getItem('db1.table1.id'), {'parent': 'db1.table1', 'name': 'id', 'type': 'uuid', 'length': 0, 'sizeof': 16, 'tags': []})
  
if __name__ == '__main__':
  unittest.main()
