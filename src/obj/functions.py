#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic
from .basicmap import BasicMap

class Function(Basic):
  def __init__ (self):
    super(Function, self).__init__(['id', 'parent', 'name', 'status', 'tags', 'description', 'input', 'output', 'use'], ['parent', 'id'], ['tags', 'input', 'output', 'use'])

class Functions(BasicMap):
  def __init__ (self):
    super(Functions, self).__init__(Function().getFields(), ['parent', 'status', 'tags'], Function())


