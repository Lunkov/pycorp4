#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic
from .basicmap import BasicMap

class System(Basic):
  def __init__ (self):
    super(System, self).__init__(['id', 'name', 'title', 'type', 'status', 'layers', 'tags', 'description', 'parent', 'git', 'wiki'], [], ['tags', 'layers'])

class Systems(BasicMap):
  def __init__ (self):
    super(Systems, self).__init__(System().getFields(), ['type', 'status', 'layers', 'tags'], System())


