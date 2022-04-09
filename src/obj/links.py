#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib

from .basic import Basic
from .basicmap import BasicMap

class Link(Basic):
  def __init__ (self):
    super(Link, self).__init__(['link_from', 'link_to', 'type', 'status', 'tags', 'link', 'group', 'description', 'comment'], ['link_from', 'link_to', 'type', 'tags'], [], 'uuid')

class Links(BasicMap):
  def __init__ (self):
    super(Links, self).__init__(Link().getFields(), ['type', 'status', 'link_from', 'link_to', 'tags'], Link())

