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

from .fs import FS
from .elog import ELog

class Uploader():
  def __init__ (self, fs, savepath, verbose):
    self.verbose = verbose
    self.initLog()
    self.savepath = savepath
    self.etc = {}
    self.fs = fs
    fileconfig = 'etc/swagger_auth.yaml'
    if os.path.isfile(fileconfig):
      with open(fileconfig, 'r') as stream:
        try:
          self.etc = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
          print("ERR: Bad format in %s: %s" % (fileconfig, exc))

  def initLog(self):
    if self.verbose >= 9:
      logging.basicConfig()
      logging.getLogger().setLevel(logging.DEBUG)
      requests_log = logging.getLogger("requests.packages.urllib3")
      requests_log.setLevel(logging.DEBUG)
      requests_log.propagate = True

  def updateSwagger(self, service):
    if len(service['swagger']) < 10:
      return False
    data, ok = self.upload(service['swagger'])
    if not ok:
      return False
    self.save(data)
  
  def getVersion(self, data):
    if not 'info' in data:
      return '0.0.0.0' 
    if not 'version' in data['info']:
      return '0.0.0.0' 
    return data['info']['version']

  def getName(self, data):
    if not 'info' in data:
      return '' 
    if not 'title' in data['info']:
      return '' 
    return data['info']['title']

  def hash(self, data):
    return hashlib.md5(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()
    
  def save(self, data):
    filename = ''
    try:
      os.makedirs("%s/%s" % (self.savepath, self.getName(data)), exist_ok=True)
      filename = "%s/%s/%s.yaml" % (self.savepath, self.getName(data), self.getVersion(data))
      re.sub('[^\w\-_\. ]', '_', filename)
      
      self.fs.writeFile(filename, yaml.dump(data))
    except Exception as e:
      print("ERR: Write File: %s: %s" % (filename, str(e)))
      return False
    return True

  def auth(self, url):
    for key, value in self.etc.items():
      if key in url:
        return value['header'], value['auth']
        break
    return {}, ()
    
  def upload(self, url):
    self.data = {}
    x = None
    contentType =  ''
    try:
      if self.verbose > 0:
        print("LOG: Download swagger from '%s'" % (url))
      header, auth = self.auth(url)
      x = requests.get(url = url, headers = header, auth = auth)
      contentType = x.headers['content-type']
    except Exception as e:
      print("ERR: HTTP '%s' (type='%s'): %s" % (url, contentType, str(e)))

    ok = False
    if (not x is None) and (x.status_code == 200):
      self.data, ok = self.parseUpload(url, contentType, x.text)

    return self.data, ok

  def parseUpload(self, url, contentType, content):
    data = {}
    contentType =  ''
    ok = False
    try:
      
      if ('application/octet-stream' in contentType) or ('.yaml' in url) or ('.yml' in url): 
        data = yaml.safe_load(content)
        return data, True
    except Exception as e:
      print("ERR: Swagger parse '%s' (type='%s'/yaml): %s" % (url, contentType, str(e)))
      if self.verbose >= 9:
        print("DBG: Swagger parse '%s': %s" % (url, content))

    try:
      if ('application/json' in contentType) or ('.json' in url)  :
        data = json.loads(content)
        ok = True
    except Exception as e:
      print("ERR: Swagger parse '%s' (type='%s'/json): %s" % (url, contentType, str(e)))
    if ok:
      print("LOG: Swagger parse '%s' OK" % (url))
    return data, ok
    

