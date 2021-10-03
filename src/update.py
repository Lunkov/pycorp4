#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import yaml
from pprint import pprint
from pathlib import Path
from .basic import Basic

class Updates(Basic):
  def __init__ (self, verbose):
    super(Updates, self).__init__()
    self.name = 'update'
    self.ids = ['name', 'service', 'version', 'plan']
    self.fields = ['id', 'code', 'name', 'service', 'plan', 'version', 'sequence', 'swagger']
    self.verbose = verbose

  def load(self, updatepath):
    fp = os.path.abspath(updatepath)
    if self.verbose:
      print("LOG: Updates: Scaning folder '%s'..." % fp)
    try:

      for path in Path(fp).rglob('*.yaml'):
        fullPath = os.path.join(fp, path.parent, path.name)
        if not os.path.isdir(fullPath):
          if self.verbose:
            print("DBG: Scan: %s" % fullPath)
          with open(fullPath, 'r') as stream:
            try:
              prop = yaml.safe_load(stream)
              key = self.genId(prop)
              prop['id'] = key
              prop['code'] = self.genCode(prop)
              if key != '':
                self.updateItem(key, prop)

            except yaml.YAMLError as err:
              print("ERR: Bad format in %s: %s" % (fullPath, str(err)))    

    except Exception as err:
      print("FATAL: Folder Not Found: %s: %s" % (fp, str(err)))

  def makeSwaggers(self):
    res = {}
    for j, up in self.getItems():
      if not 'swagger' in up:
        continue
      k = up.get('service', ''), up.get('version', '')
      if not k in res:
        item = {}
        item['swagger'] = '2.0'
        item['info'] = {}
        item['info']['version'] = up.get('version', '')
        item['info']['title'] = up.get('service', '')
        item['schemes'] = []
        item['consumes'] = []
        item['produces'] = []
        item['paths'] = {}
        item['definitions'] = {}
        res[k] = item
      item = res[k]
      if 'schemes' in up['swagger']:
        item['schemes'].update(up['swagger']['schemes'])
      
      if 'consumes' in up['swagger']:
        item['consumes'].update(up['swagger']['consumes'])
      
      if 'produces' in up['swagger']:
        item['produces'].update(up['swagger']['produces'])
      
      if 'paths' in up['swagger']:
        item['paths'].update(up['swagger']['paths'])
      
      if 'definitions' in up['swagger']:
        item['definitions'].update(up['swagger']['definitions'])
      res[k] = item
    return res

  def graphSequence(self, D, seq, services):
    if hasattr(seq['sequence'], "__len__"):
      for v in seq['sequence']:
        pprint(v)
        '''
        service = services.getItem(v.get('from', 'undef'))
        if service:
          D.node(service.get('id', 'xz'),
                 service.get('name', 'xz'),
                 'main', 
                 service.get('type', 'service'),
                 service.get('status', 'undef'),
                 service.get('link', ''),
                 service.get('description', ''))
        '''
        D.sequence('main', v.get('from', 'undef'), v.get('to', 'undef'), v.get('api', 'undef'), v.get('type', 'ok'))
