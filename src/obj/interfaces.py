#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic
from .basicmap import BasicMap

class Interface(Basic):
  def __init__ (self):
    super(Interface, self).__init__(['id', 'name', 'title', 'system', 'status', 'tags', 'description', 'comment'], [], ['tags'])

class Interfaces(BasicMap):
  def __init__ (self):
    super(Interfaces, self).__init__(Interface().getFields(), ['type', 'status', 'layer', 'tags'], Interface())


