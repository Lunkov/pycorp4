#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import yaml
from pathlib import Path
from .basic import Basic
from .swagger import Swagger

class Swaggers(Basic):
  def __init__ (self, verbose):
    super(Swaggers, self).__init__()
    self.m = {}
    self.name = 'swaggers'
    self.ids = ['service', 'version']
    self.fields = ['id', 'service', 'plan', 'fact', 'version', 'swagger-data', 'hash']
    self.verbose = verbose

  def load(self, swaggerpath):
    fp = os.path.abspath(swaggerpath)
    fsws = '%s.all.json' % fp
    if self.verbose:
      print("LOG: Swaggers read '%s'..." % fsws)
    self.readJSON(fsws)
    if self.verbose:
      print("LOG: Swaggers: Scaning folder '%s'..." % fp)
    try:
      sw = Swagger(self.verbose)
      for path in Path(fp).rglob('*.yaml'):
        fullPath = os.path.join(fp, path.parent, path.name)
        if os.path.isfile(fullPath):
          sw.loadYAML(fullPath)

          prop = {}
          prop['version'] = sw.getVersion()
          prop['service'] = sw.getName()
          prop['swagger-data'] = sw.get()
          prop['plan'] = False
          prop['fact'] = True
          # key = self.genId(prop)
          key = sw.hash()
          prop['id'] = key
          prop['hash'] = sw.hash()
          
          if key != '':
            self.addItem(key, prop)

    except Exception as err:
      print("FATAL: File(%s): %s" % (fullPath, str(err)))

    if self.verbose:
      print("LOG: Swaggers write '%s'..." % fsws)
    self.writeJSON(fsws)

  def updateSwagger(self, service, sw):
    if service['swagger'] == '':
      print("SWAGGER NOT FOUND for %s" % (service['name']))
      return False

    print("DBG: Upload swagger: %s -> %s" % (service['name'], service['swagger']))
    data, ok = sw.upload(service['swagger'])
    if not ok:
      print("ERR: Load swagger: %s -> %s" % (service['name'], service['swagger']))
      elog = ELog()
      elog.log("HTTP_ERROR", ("ERR: Load swagger: %s -> %s" % (service['name'], service['swagger'])), service['name'], service['swagger'])
      return False
    description = ''
    if 'description' in data['info']:
      description = data['info']['description']
    for path, va in  data['paths'].items():
      for method, vm in  va.items():
        desc = description
        if 'description' in vm:
          desc = vm['description']
        ida = service['name'] + '.' + method.upper() + '.' + path
        title = method.upper() + ' ' + path
        self.api.addItem(ida, { 'title': title, 'service': service['name'], 'method': method.upper(), 'url': path, 'description': desc} )
    return True
