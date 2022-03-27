#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib

from .basic import Basic
from .basicmap import BasicMap

class Link(Basic):
  def __init__ (self):
    super(Link, self).__init__(['item_from', 'item_to', 'type', 'status', 'tags', 'link', 'group', 'description', 'comment'], ['item_from', 'item_to', 'type', 'tags'], [])

class Links(BasicMap):
  def __init__ (self):
    super(Links, self).__init__(Link().getFields(), ['type', 'status', 'item_from', 'item_to', 'tags'], Link())

