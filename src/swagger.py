#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import codecs
import re
import logging
import requests
import json
from csv import reader
from urllib.parse import urlencode, quote
from pprint import pprint
import yaml

from .elog import ELog

class Swagger():
  def __init__ (self):
    self.data = {}
    self.etc = {}
    fileconfig = 'etc/swagger_auth.yaml'
    if os.path.isfile(fileconfig):
      with open(fileconfig, 'r') as stream:
        try:
          self.etc = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
          print("ERR: Bad format in %s: %s" % (fileconfig, exc))

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

  def save(self, dt):
    filename = ''
    try:
      os.makedirs("html/swagger/%s" % (self.getName()))
      filename = "html/swagger/%s/%s-%s.yaml" % (self.getName(), dt, self.getVersion())
      re.sub('[^\w\-_\. ]', '_', filename)
      file = codecs.open(filename, 'w', 'utf-8')
      yaml.dump(self.data, file)
      file.close()
    except Exception as e:
      print("ERR: Write File: %s: %s" % (filename, str(e)))

  def auth(self, url):
    for key, value in self.etc.items():
      if key in url:
        return value['header'], value['auth']
        break
    return {}, ()
    
  def load(self, url):
    self.data = {}
    x = None
    contentType =  ''
    try:
      header, auth = self.auth(url)
      x = requests.get(url = url, headers = header, auth = auth)
      contentType = x.headers['content-type']
    except Exception as e:
      print("ERR: HTTP '%s' (type='%s'): %s" % (url, contentType, str(e)))
    
    ok = False
    if (not x is None) and (x.status_code == 200):
      self.data, ok = self.parse(url, contentType, x.text)

    if not ok:
      print("ERR: Swagger parse '%s': %s" % (url, x))
      
    return self.data, ok
  
  
  def parse(self, url, contentType, content):
    data = {}
    contentType =  ''
    ok = False
    try:
      print(contentType)
      if ('application/octet-stream' in contentType) or ('.yaml' in url) or ('.yml' in url): 
        data = yaml.safe_load(content)
        ok = True
    except Exception as e:
      print("ERR: Swagger parse '%s' (type='%s'/yaml): %s" % (url, contentType, str(e)))

    try:
      if (len(data) < 1) and (('application/json' in contentType) or ('.json' in url)):
        data = json.loads(content)
        ok = True
    except Exception as e:
      print("ERR: Swagger parse '%s' (type='%s'/json): %s" % (url, contentType, str(e)))
    if ok:
      print("LOG: Swagger parse '%s' OK" % (url))
    return data, ok
    
  def compare(self, swg):
    c = {}
    if self.getVersion() != swg.getVersion():
      c['version'] = {'swagger1': self.getVersion(), 'swagger2': swg.getVersion()}
    
    d = swg.get()
    c['path_new'] = {}
    for k, v in self.data['paths'].items():
      if not k in d['paths']:
        c['path_new'][k] = v
      else:
        for kp, vp in v.items():
          if not kp in d['paths'][k]:
            c['path_new'][k] = v
          
    c['path_depricated'] = {}
    for k, v in d['paths'].items():
      if not k in self.data['paths']:
        c['path_depricated'][k] = v
      else:
        for kp, vp in v.items():
          if not kp in self.data['paths'][k]:
            c['path_depricated'][k] = v
    
    c['components_new'] = {}
    for k, v in self.data['components']['schemas'].items():
      if not k in d['components']['schemas']:
        c['components_new'][k] = v
    c['components_depricated'] = {}
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
