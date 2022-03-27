#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic
from .basicmap import BasicMap


class Node(Basic):
  def __init__ (self):
    super(Node, self).__init__(['id', 'name', 'title', 'domain', 'type', 'status', 'layers', 'tags', 'description', 'mem', 'cpu', 'hdd', 'net'], [], ['tags', 'layers'])

class Nodes(BasicMap):
  def __init__ (self):
    super(Nodes, self).__init__(Node().getFields(), ['type', 'status', 'layers', 'tags'], Node())


