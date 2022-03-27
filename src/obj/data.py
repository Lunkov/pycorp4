#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic
from .basicmap import BasicMap


class DataSet(Basic):
  def __init__ (self):
    super(DataSet, self).__init__(['id', 'name', 'sizeof', 'tags'], [], ['tags'])

class DataSets(BasicMap):
  def __init__ (self):
    super(DataSets, self).__init__(DataSet().getFields(), [], DataSet())

class DataField(Basic):
  def __init__ (self):
    super(DataField, self).__init__(['id', 'name', 'data', 'type', 'tags', 'length', 'sizeof'], ['data', 'id'], ['tags'])

  def set(self, properties: dict):
    if not 'sizeof' in properties:
      if 'type' in properties:
        if properties['type'] == 'string':
          if 'length' in properties:
            properties['sizeof'] = (int(properties['length']) + 1) * 2  #utf-8
          else:
            properties['sizeof'] = 256
        if properties['type'] == 'int':
          properties['sizeof'] = 4
        if properties['type'] == 'float':
          properties['sizeof'] = 4
        if properties['type'] == 'double':
          properties['sizeof'] = 8
    return super().set(properties)

class DataFields(BasicMap):
  def __init__ (self):
    super(DataFields, self).__init__(DataField().getFields(), [], DataField())
