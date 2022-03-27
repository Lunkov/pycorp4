#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from  pprint import pprint
from  src.obj.basic import Basic
from  src.obj.basicmap import BasicMap

class TSystem(Basic):
  def __init__ (self):
    super(TSystem, self).__init__(['id', 'name', 'tags'], [], ['tags'])

class TSystems(BasicMap):
  def __init__ (self):
    super(TSystems, self).__init__(TSystem().getFields(), ['type', 'status', 'layers', 'tags'], TSystem())

class TestBasic(unittest.TestCase):

  def testBasic(self):
    srv = TSystems()
    srv.append(TSystem().set({'id': 'sr1', 'name': 'Service 1', 'tags': ['price', 'product']}))
    srv.append(TSystem().set({'id': 'sr2', 'name': 'Service 2', 'tags': ['price']}))
    srv.append(TSystem().set({'id': 'sr3', 'name': 'Service 3', 'tags': ['product']}))
    srv.append(TSystem().set({'id': 'sr4', 'name': 'Service 4', 'tags': 'product'}))
    srv.append(TSystem().set({'id': 'sr6', 'name': 'Service 6', 'tags': ''}))

    srv.append(TSystem().set({'id': 'sr5', 'tags': 'product'}))
    srv.append(TSystem().set({'id': 'sr5', 'name': 'Service 5', 'tags': 'plp,pdp,product'}))
    self.assertEqual(srv.getItem('sr5'), {'id': 'sr5', 'name': 'Service 5', 'tags': ['plp', 'pdp', 'product']})
    
    self.assertEqual(srv.count(), 6)
    self.assertEqual(srv.__class__.__name__, 'TSystems')
    
    srv2 = srv.clone()
    self.assertEqual(srv2.count(), 0)
    self.assertEqual(srv2.__class__.__name__, 'TSystems')

  def testBasicMapFilters(self):
    self.maxDiff = None
    srv = TSystems()
    
    srv.append(TSystem().set({'id': 'sr1', 'name': 'Service 1', 'tags': ['price', 'product']}))
    srv.append(TSystem().set({'id': 'sr2', 'name': 'Service 2', 'tags': ['price']}))
    srv.append(TSystem().set({'id': 'sr3', 'name': 'Service 3', 'tags': ['product']}))
    srv.append(TSystem().set({'id': 'sr4', 'name': 'Service 4', 'tags': 'product'}))
    srv.append(TSystem().set({'id': 'sr5', 'name': 'Service 5', 'tags': 'plp,pdp,product'}))
    srv.append(TSystem().set({'id': 'sr6', 'name': 'Service 6', 'tags': ''}))

    srv_empty = srv.filter('ts', 'price')
    self.assertEqual(srv_empty.get(), {})
    
    srv_price = srv.filter('tags', 'price')
    
    self.assertEqual(srv_price.get(), {'sr1': {'id': 'sr1', 'name': 'Service 1', 'tags': ['price', 'product']},
                                 'sr2': {'id': 'sr2', 'name': 'Service 2', 'tags': ['price']}
    })

    srv_prod = srv.filter('tags', ['price', 'product'])
    self.assertEqual(srv_prod.get(), {'sr1': {'id': 'sr1', 'name': 'Service 1', 'tags': ['price', 'product']},
                                 'sr2': {'id': 'sr2', 'name': 'Service 2', 'tags': ['price']},
                                 'sr3': {'id': 'sr3', 'name': 'Service 3', 'tags': ['product']},
                                 'sr4': {'id': 'sr4', 'name': 'Service 4', 'tags': ['product']},
                                 'sr5': {'id': 'sr5', 'name': 'Service 5', 'tags': ['plp', 'pdp', 'product']}
    })

    srv_plp = srv.filter('tags', 'plp')
    
    self.assertEqual(srv_plp.get(), {'sr5': {'id': 'sr5', 'name': 'Service 5', 'tags': ['plp', 'pdp', 'product']}
    })


    srv_plp = srv.filter('tags', ['plp'])
    
    self.assertEqual(srv_plp.get(), {'sr5': {'id': 'sr5', 'name': 'Service 5', 'tags': ['plp', 'pdp', 'product']}
    })
    
if __name__ == '__main__':
  unittest.main()
