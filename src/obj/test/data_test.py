#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from  pprint import pprint
from  src.obj.data import DataField, DataFields

class TestData(unittest.TestCase):

  def testData(self):
    flds = DataFields()
    
    flds.append(DataField().set({'data': 'msg_price', 'id': 'id_currency', 'name': 'currency', 'type': 'string', 'length': '3', 'tags': 'price'}))
    flds.append(DataField().set({'data': 'msg_price', 'id': 'price', 'name': 'price', 'type': 'float', 'tags': 'price'}))

    self.assertEqual(flds.count(), 2)
    self.assertEqual(flds.getName(), 'DataFields')
    
    self.assertEqual(flds.getItem('id_currency'), {'data': 'msg_price', 'id': 'id_currency', 'length': '3', 'name': 'currency', 'sizeof': 8, 'tags': ['price'], 'type': 'string'})
    self.assertEqual(flds.getItem('price'), {'data': 'msg_price', 'id': 'price', 'name': 'price', 'sizeof': 4, 'tags': ['price'], 'type': 'float'})

    
if __name__ == '__main__':
  unittest.main()
