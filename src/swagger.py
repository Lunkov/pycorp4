#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import codecs
import re
import logging
import requests
import json
import yaml
import hashlib
from csv import reader
from urllib.parse import urlencode, quote
from pprint import pprint

from .elog import ELog

class Swagger():
  def __init__ (self, verbose):
    self.verbose = verbose
    self.data = {}

  def get(self):
    return self.data
    
  def getVersion(self):
    if not 'info' in self.data:
      return '0.0.0.0' 
    if not 'version' in self.data['info']:
      return '0.0.0.0' 
    return self.data['info']['version']

  def getName(self):
    if not 'info' in self.data:
      return '' 
    if not 'title' in self.data['info']:
      return '' 
    return self.data['info']['title']

  def hash(self):
    return hashlib.md5(json.dumps(self.data, sort_keys=True).encode('utf-8')).hexdigest()

  def loadYAML(self, filename):
    self.data = {}
    if self.verbose:
      print("LOG: Swagger load '%s'..." % filename)

      try:
        with codecs.open(filename, 'r', encoding='utf-8') as stream:
          self.data = yaml.safe_load(stream)

      except yaml.YAMLError as exc:
        print("ERR: Bad format in %s: %s" % (filename, exc))        
        return {}, False

    return self.data, True

  def compare(self, swg):
    c = {}
    if self.getVersion() != swg.getVersion():
      c['version'] = {'swagger1': self.getVersion(), 'swagger2': swg.getVersion()}
    
    d = swg.get()
    c['path_new'] = {}
    if 'paths' in self.data:
      for k, v in self.data['paths'].items():
        if not k in d['paths']:
          c['path_new'][k] = v
        else:
          for kp, vp in v.items():
            if not kp in d['paths'][k]:
              c['path_new'][k] = v
          
    c['path_depricated'] = {}
    if 'paths' in d:
      for k, v in d['paths'].items():
        if not k in self.data['paths']:
          c['path_depricated'][k] = v
        else:
          for kp, vp in v.items():
            if not kp in self.data['paths'][k]:
              c['path_depricated'][k] = v
    
    c['components_new'] = {}
    if 'components' in self.data:
      for k, v in self.data['components']['schemas'].items():
        if not k in d['components']['schemas']:
          c['components_new'][k] = v
    c['components_depricated'] = {}
    if 'components' in d:
      for k, v in d['components']['schemas'].items():
        if not k in self.data['components']['schemas']:
          c['components_depricated'][k] = v
    return c

  def htmlCompare(self, c):
    p = "<h1>Сравнение API '%s'</h1>" % self.getName()
    p = p + "<h2>Новые API</h2>"
    for k, v in c['path_new'].items():
      p = p + self.htmlPath(k)
    p = p + "<h2>Удалённые API</h2>"
    for k, v in c['components_depricated'].items():
      p = p + self.htmlPath(k)
    p = p + "<h2>Новые структуры данных</h2>"
    for k, v in c['components_new'].items():
      p = p + self.htmlComponent(k)
    p = p + "<h2>Удалённые структуры данных</h2>"
    for k, v in c['components_depricated'].items():
      p = p + self.htmlComponent(k)
    return p

  def htmlComponent(self, name):
    if not name in self.data['components']['schemas']:
      return ''
    p = "<h3>%s</h3>" % name
    p = p + "<table class='table'>"
    p = p + "<tr><td>Наименование</td><td>Тип</td><td>Описание</td></tr>"
    for k, v in self.data['components']['schemas'][name]['properties'].items():
      p = p + "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (k, v.get('type', ''), v.get('description', ''))
    p = p + "</table>"
    return p

  def htmlPath(self, name):
    if not name in self.data['paths']:
      return ''
    p = "<h3>%s</h3>" % name
    p = p + "<table class='table'>>"
    p = p + "<tr><td>Метод</td><td>Тэг</td><td>Описание</td></tr>"
    for k, v in self.data['paths'][name].items():
      p = p + "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (k, v.get('tags', ''), v.get('description', ''))
    p = p + "</table>"
    return p
