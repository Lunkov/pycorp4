#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import sys
import os
from src.load.topics import ImportXLS
from src.workspace import Workspace

class TestImportData(unittest.TestCase):

  def testTopics(self):

    w = Workspace('test', None, True)
    ix = ImportXLS()
    ok = ix.loadTopics('src/load/test/data/Topics.xlsx', w)
    
    self.assertEqual(ok, True)
    self.assertEqual(w.getSystems().count(), 27)
    self.assertEqual(w.getSystems().getItem('Service 1'), {'id': 'Service 1', 'layers': [], 'tags': ['tag1'], 'type': 'microservice'})

  
if __name__ == '__main__':
  unittest.main()
