#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic
from .basicmap import BasicMap


class Tag(Basic):
  def __init__ (self):
    super(Tag, self).__init__(['id', 'name'], [], [])

class Tags(BasicMap):
  def __init__ (self):
    super(Tags, self).__init__(Tag().getFields(), [], Tag())
