#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from ..basic import Basic

    
class TestServices(Basic):
  def __init__ (self, api):
    super(TestServices, self).__init__()
    self.name = 'services'
    self.fields = ['id', 'name', 'tags']
    self.api = api

class TestBasic(unittest.TestCase):

  def testServicesTags(self):
    self.maxDiff = None
    srv = TestServices(None)
    
    srv.addItem('srv1', {'id': 'sr1', 'name': 'Service 1', 'tags': ['price', 'product']})
    srv.addItem('srv2', {'id': 'sr2', 'name': 'Service 2', 'tags': ['price']})
    srv.addItem('srv3', {'id': 'sr3', 'name': 'Service 3', 'tags': ['product']})
    srv.addItem('srv4', {'id': 'sr4', 'name': 'Service 4', 'tags': 'product'})
    srv.addItem('srv5', {'id': 'sr5', 'name': 'Service 5', 'tags': 'plp,pdp,product'})
    srv.addItem('srv6', {'id': 'sr6', 'name': 'Service 6', 'tags': ''})
		
    srv_empty = srv.filter('ts', 'price')
    self.assertEqual(srv_empty, {})
    
    srv_price = srv.filter('tags', 'price')
    
    self.assertEqual(srv_price, {'srv1': {'id': 'sr1', 'name': 'Service 1', 'tags': ['price', 'product']},
                                 'srv2': {'id': 'sr2', 'name': 'Service 2', 'tags': ['price']}
    })
    
    srv_prod = srv.filter('tags', ['price', 'product'])
    
    self.assertEqual(srv_prod, {'srv1': {'id': 'sr1', 'name': 'Service 1', 'tags': ['price', 'product']},
                                 'srv2': {'id': 'sr2', 'name': 'Service 2', 'tags': ['price']},
                                 'srv3': {'id': 'sr3', 'name': 'Service 3', 'tags': ['product']},
                                 'srv4': {'id': 'sr4', 'name': 'Service 4', 'tags': ['product']},
                                 'srv5': {'id': 'sr5', 'name': 'Service 5', 'tags': ['plp', 'pdp', 'product']}
    })

    srv_plp = srv.filter('tags', 'plp')
    
    self.assertEqual(srv_plp, {'srv5': {'id': 'sr5', 'name': 'Service 5', 'tags': ['plp', 'pdp', 'product']}
    })


    srv_plp = srv.filter('tags', ['plp'])
    
    self.assertEqual(srv_plp, {'srv5': {'id': 'sr5', 'name': 'Service 5', 'tags': ['plp', 'pdp', 'product']}
    })
    
if __name__ == '__main__':
  unittest.main()
