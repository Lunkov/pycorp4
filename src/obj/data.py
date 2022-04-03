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
    super(DataField, self).__init__(['id', 'name', 'parent', 'type', 'tags', 'length', 'sizeof', 'required'], ['parent', 'name'], ['tags'])

  def set(self, properties: dict):
    if not 'sizeof' in properties:
      if 'type' in properties:
        ft = properties['type']
        if ft == 'string' or ft == 'varchar':
          if 'length' in properties:
            properties['sizeof'] = (int(properties['length']) + 1) * 2  #utf-8
          else:
            properties['sizeof'] = 256
        if ft == 'bool' or ft == 'boolean':
          properties['sizeof'] = 1
        if ft == 'int':
          properties['sizeof'] = 4
        if ft == 'bigint':
          properties['sizeof'] = 4
        if ft == 'float':
          properties['sizeof'] = 4
        if ft == 'double':
          properties['sizeof'] = 8
        if ft == 'date':
          properties['sizeof'] = 4
        if ft == 'timestamp':
          properties['sizeof'] = 8
        if ft == 'uuid':
          properties['sizeof'] = 16
    return super().set(properties)

class DataFields(BasicMap):
  def __init__ (self):
    super(DataFields, self).__init__(DataField().getFields(), [], DataField())
