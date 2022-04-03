#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import sys
import os
import json
import filecmp
from pprint import pprint
from src.workspace import Workspace
from src.helpers.fs import FS
from src.dia.mermaid import Mermaid
from src.dia.universedia import UniverseDia
from src.obj.systems import System
from src.obj.links import Link
from src.obj.data import DataSet, DataSets, DataField, DataFields

class TestDiagram(unittest.TestCase):

  def setUp(self):
    self.fs = FS()
    
    self.w = Workspace('test', self.fs, '', 0)
    
    self.w.getSystems().append(System().set({'id': 'srv.1', 'name': 'srv.1', 'type': 'microservice', 'tags': 'price'}))
    self.w.getSystems().append(System().set({'id': 'srv.2', 'name': 'srv.2', 'type': 'microservice', 'tags': 'price'}))
    self.w.getSystems().append(System().set({'id': 'srv.3', 'name': 'srv.3', 'type': 'microservice', 'tags': 'price'}))
    self.w.getSystems().append(System().set({'id': 'topic.1', 'name': 'topic.1', 'type': 'kafka-topic', 'tags': 'price'}))
    
    self.w.getLinks().append(Link().set({'item_from': 'srv.1',
                                    'item_to': 'topic.1',
                                    'type': 'data',
                                    'tags': 'price'}))

    self.w.getLinks().append(Link().set({'item_from': 'topic.1',
                                    'item_to': 'srv.2',
                                    'type': 'data',
                                    'tags': 'price'}))

    self.w.getLinks().append(Link().set({'item_from': 'topic.1',
                                    'item_to': 'srv.3',
                                    'type': 'data',
                                    'tags': 'price'}))

    self.w.getDataSets().append(DataSet().set({'id': 'msg_price', 'name': 'msg_price', 'type': 'struct', 'tags': 'price', 'sizeof': 256}))
    self.w.getDataFields().append(DataField().set({'data': 'msg_price', 'id': 'id_currency', 'name': 'currency', 'type': 'string', 'length': '3', 'tags': 'price'}))
    self.w.getDataFields().append(DataField().set({'data': 'msg_price', 'id': 'price', 'name': 'price', 'type': 'float', 'length': '8', 'tags': 'price'}))
    self.w.getDataSets().append(DataSet().set({'id': 'msg_price_full', 'name': 'msg_price_full', 'type': 'struct', 'tags': 'price'}))

    self.w.getLinks().append(Link().set({'item_from': 'msg_price',
                                    'item_to': 'msg_price_full',
                                    'type': 'dataflow',
                                    'description': 'price',
                                    'tags': 'price'}))
    

  
  def testDiaFlow(self):

    dia = Mermaid({})
    dia.new('flowLR', 'all')

    for i, node in self.w.getSystems().get().items():
      dia.node(i, node.get('name', ''), 'area 1', node.get('type', ''), '', '', '')

    for i, link in self.w.getLinks().get().items():
      if link.get('type', '') != 'dataflow':
        dia.link(link.get('item_from', 'xz'),
                 link.get('item_to', 'xz'),
                 link.get('domain', ''),
                 link.get('tags', ''),
                 link.get('status', ''),
                 link.get('description', ''))

    res = dia.finish()
        
    self.assertEqual(res, 'flowchart LR\n'
        '    0f3f9cd59b3706accf254b9594b528e6["srv.1"]\n'
        '    036985dbc4ae9b679aa0e499c46663a1["srv.2"]\n'
        '    d02285272c6bf2781ce6a18f61e7797c["srv.3"]\n'
        '    044b03ca776d8088f333cd2a3eeb62ca["topic.1"]\n'
        '    0f3f9cd59b3706accf254b9594b528e6 -...- 044b03ca776d8088f333cd2a3eeb62ca\n'
        '    044b03ca776d8088f333cd2a3eeb62ca -...- 036985dbc4ae9b679aa0e499c46663a1\n'
        '    044b03ca776d8088f333cd2a3eeb62ca -...- d02285272c6bf2781ce6a18f61e7797c\n')

  def testDiaData(self):

    dia = Mermaid({})
    dia.new('data', 'all')

    for i, dataSet in self.w.getDataSets().get().items():
      dia.data(i, dataSet.get('name', ''), 'area 1', dataSet.get('type', ''), dataSet.get('sizeof', 0))

    for i, dataField in self.w.getDataFields().get().items():
      dia.dataFields(dataField.get('data', 'undef'), i, dataField.get('type', ''))

    for i, link in self.w.getLinks().get().items():
      if link.get('type', '') == 'dataflow':
        dia.dataLink(link.get('item_from', 'xz'),
                 link.get('item_to', 'xz'),
                 link.get('type', ''),
                 link.get('description', ''))

    res = dia.finish()

    self.assertEqual(res, 'classDiagram\n'
        '  direction RL\n'
        '    class msg_price{\n'
        '    sizeof(256)\n'
        '    id_currency : string\n'
        '    price : float\n'
        '    }\n'
        '    class msg_price_full{\n'
        '    }\n'
        '    msg_price "" --> "" msg_price_full : price\n')

  def testUniverseDia(self):
    dia = UniverseDia(self.fs, None, None, True)
    dia.drawBlockDiagram('Test Dia', self.w, None, self.w.getSystems().get(), self.w.getLinks().filter('type', 'data').get(), 'src/dia/test/data/test1')
    
    self.assertEqual(True, filecmp.cmp('src/dia/test/data/test1_need.mmd', 'src/dia/test/data/test1.mmd'))
    os.remove('src/dia/test/data/test1.mmd')

  
if __name__ == '__main__':
  unittest.main()
