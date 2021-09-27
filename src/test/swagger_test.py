#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from ..basic import Basic
from ..swagger import Swagger

    
class TestSwagger(unittest.TestCase):

  def testUpload(self):
    s = Swagger()

    url = 'github.com'
    header, auth = s.auth(url)
    self.assertEqual(header, {})
    self.assertEqual(auth, ())

    s.etc = {'github': {'header': {'Authorization': 'token 3423432'}, 'auth': ()},
             'gitlab': {'header': {}, 'auth': ('user', 'pwd')},}

    url = 'github.com'
    header, auth = s.auth(url)
    self.assertEqual(header, {'Authorization': 'token 3423432'})
    self.assertEqual(auth, ())

    url = 'https://github.com/12345'
    header, auth = s.auth(url)
    self.assertEqual(header, {'Authorization': 'token 3423432'})
    self.assertEqual(auth, ())

    url = 'https://gitlab.com/12345'
    header, auth = s.auth(url)
    self.assertEqual(header, {})
    self.assertEqual(auth, ('user', 'pwd'))

    
if __name__ == '__main__':
  unittest.main()
