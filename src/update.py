#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import yaml
import codecs
from pprint import pprint
from pathlib import Path
from .basic import Basic

class Updates(Basic):
  def __init__ (self, verbose):
    super(Updates, self).__init__()
    self.name = 'update'
    self.ids = ['name', 'service', 'version', 'plan']
    self.fields = ['id', 'code', 'name', 'service', 'url', 'plan', 'version', 'sequence', 'status', 'swagger', 'swagger-api', 'swagger-api-method', 'swagger-api-parameters', 'swagger-api-response', 'swagger-api-description', 'errors']
    self.verbose = verbose

  def updateProp(self, prop):
    if 'swagger' in prop:
      if 'paths' in prop['swagger']:
        if len(prop['swagger']['paths']) > 0:
          prop['swagger-api'] = next(iter(prop['swagger']['paths']))
          if len(prop['swagger']['paths'][prop['swagger-api']]) > 0:
            prop['swagger-api-method'] = next(iter(prop['swagger']['paths'][prop['swagger-api']]))
            if 'description' in prop['swagger']['paths'][prop['swagger-api']][prop['swagger-api-method']]:
              prop['swagger-api-description'] = prop['swagger']['paths'][prop['swagger-api']][prop['swagger-api-method']]['description']
            if 'parameters' in prop['swagger']['paths'][prop['swagger-api']][prop['swagger-api-method']]:
              prop['swagger-api-parameters'] = prop['swagger']['paths'][prop['swagger-api']][prop['swagger-api-method']]['parameters']
            if 'responses' in prop['swagger']['paths'][prop['swagger-api']][prop['swagger-api-method']]:
              prop['swagger-api-responses'] = prop['swagger']['paths'][prop['swagger-api']][prop['swagger-api-method']]['responses']
    return prop

  def load(self, updatepath):
    fp = os.path.abspath(updatepath)
    if self.verbose > 0:
      print("LOG: Updates: Scaning folder '%s'..." % fp)
    try:

      for path in Path(fp).rglob('*.yaml'):
        fullPath = os.path.join(fp, path.parent, path.name)
        if not os.path.isdir(fullPath):
          if self.verbose > 5:
            print("DBG: Scan: %s" % fullPath)
          try:
            with codecs.open(fullPath, 'r', encoding='utf-8') as stream:
              prop = yaml.safe_load(stream)
              key = self.genId(prop)
              prop['id'] = key
              prop['code'] = self.genCode(prop)
              if key != '':
                self.updateItem(key, self.updateProp(prop))

          except yaml.YAMLError as err:
            print("ERR: Bad format in %s: %s" % (fullPath, str(err)))    

    except Exception as err:
      print("FATAL: Folder Not Found: %s: %s" % (fp, str(err)))

  def makeSwaggers(self):
    res = {}
    for j, up in self.getItems():
      if not up or not 'swagger' in up:
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

  def calc(self, services):
    res = {}
    for j, up in self.getItems():
      if not up or not 'sequence' in up:
        continue
      if not 'service' in up:
        continue
      s = up['service']
      self.m[j]['max-rps-calc'] = 9999999999
      self.m[j]['max-rps-high-calc'] = 9999999999
      self.m[j]['rt99-calc'] = 0
      self.m[j]['rt95-calc'] = 0
      self.m[j]['5xx-calc'] = 0
      for k, v in enumerate(up['sequence']):
        if not 'status' in v:
          v['status'] = ''
        status = v['status']
        srv1 = services.getItem(v.get('from', ''))
        srv2 = services.getItem(v.get('to', ''))
        if not srv1:
          status = status + ('Сервис "%s" не  найден' % v.get('from', ''))
        if not srv2:
          status = status + ('Сервис "%s" не  найден' % v.get('to', ''))
        if srv1 and srv2:
          if s == v.get('from', ''):
            maxrps = 0
            try:
              maxrps = int(srv2.get('max_rps', '0'))
            except ValueError:
              pass
            if self.m[j]['max-rps-calc'] > maxrps:
              self.m[j]['max-rps-calc'] = maxrps
            maxrps = 0
            try:
              maxrps = int(srv2.get('max_rps_high', '0'))
            except ValueError:
              pass
            if self.m[j]['max-rps-high-calc'] > maxrps:
              self.m[j]['max-rps-high-calc'] = maxrps
            try:
              rt99 = int(srv2.get('rt_99', '0'))
              self.m[j]['rt99-calc'] = self.m[j]['rt99-calc'] + rt99
            except ValueError:
              pass
            try:
              rt95 = int(srv2.get('rt_95', '0'))
              self.m[j]['rt95-calc'] = self.m[j]['rt95-calc'] + rt95
            except ValueError:
              pass

        self.m[j]['sequence'][k]['status'] = status

      if self.m[j]['max-rps-calc'] == 9999999999:
        self.m[j]['max-rps-calc'] = 'не определено'
      if self.m[j]['max-rps-high-calc'] == 9999999999:
        self.m[j]['max-rps-high-calc'] = 'не определено'
      if self.m[j]['rt99-calc'] == 0:
        self.m[j]['rt99-calc'] = 'не определено'
      if self.m[j]['rt95-calc'] == 0:
        self.m[j]['rt95-calc'] = 'не определено'
      if self.m[j]['5xx-calc'] == 0:
        self.m[j]['5xx-calc'] = 'не определено'
