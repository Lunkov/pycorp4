#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path
import pylightxl as xl

from urllib.parse import urlencode, quote
from pprint import pprint
from datetime import date

from .obj.domains import Domains
from .obj.tags import Tags
from .obj.services import Services
from .obj.nodes import Nodes
from .obj.links import Links
from .fs import FS

import re


class Workspaces():
  def __init__ (self, fs, config, verbose):
    self.fs = fs
    self.config = config
    self.verbose = verbose
    
    self.m = {}
    self.domains = Domains()
    self.services = Services()
    self.nodes = Nodes()
    self.links = Links()
    self.tags = Tags()

  def reload(self, iw):
    w = self.config.getCfg('workspaces')
    if iw in w:
      self.loadYAML(iw, w[iw]['path'])

  def loads(self):
    ws = self.config.getCfg('workspaces')
    for iw, wv in ws.items():
      if 'path' in wv:
        self.load(iw, wv['path'])

  def dump(self, iw, path):
    self.m[iw]['domains'].dumpCSV('%s/data/%s/domains.csv' % (path, iw))
    self.m[iw]['services'].dumpCSV('%s/data/%s/services.csv' % (path, iw))
    self.m[iw]['links'].dumpCSV('%s/data/%s/links.csv' % (path, iw))
  
  def load(self, iw, path):
    self.m[iw] = {}
    self.m[iw]['domains'] = Domains()
    self.m[iw]['services'] = Services()
    self.m[iw]['links'] = Links()
    self.m[iw]['tags'] = Tags()
    self.loadXLSs(iw, path)
    self.m[iw]['domains'].loadFromPath(path, '*.domain', self.verbose)
    self.m[iw]['services'].loadFromPath(path, '*.service', self.verbose)
    self.m[iw]['links'].loadFromPath(path, '*.link', self.verbose)
    self.m[iw]['tags'].loadFromPath(path, '*.tag', self.verbose)

  def loadXLSs(self, iw, pathname):
    fp = os.path.abspath(pathname)
    fullPath = fp
    if self.verbose:
      print("LOG: XLSs read from '%s'..." % fp)
    try:
      for path in Path(fp).rglob('*.xlsx'):
        fullPath = os.path.join(fp, path.parent, path.name)
        if os.path.isfile(fullPath):
          self.loadXLS(iw, fullPath)
          
    except Exception as err:
      print("FATAL: File(%s): %s" % (fullPath, str(err)))
    
  def loadXLS(self, iw, filename):
    if self.verbose:
      print("LOG: Reading '%s'..." % filename)
    db = xl.readxl(fn=filename)
    self.m[iw]['domains'].readXLS(db, 'DOMAINS')
    self.m[iw]['tags'].readXLS(db, 'TAGS')
    self.m[iw]['services'].readXLS(db, 'SERVICES')
    self.m[iw]['links'].readXLS(db, 'LINKS')
    if self.verbose:
      print("LOG: Read '%s' - OK" % filename)

  def exists(self, ws):
    return ws in self.m

  def getStat(self, iw):
    if iw in self.m:
      w = self.config.getCfg('workspaces')
      return {  'cnt_domains': self.m[iw]['domains'].getCount(),
                'cnt_tags': self.m[iw]['tags'].getCount(),
                'cnt_services': self.m[iw]['services'].getCount(),
                'cnt_links': self.m[iw]['links'].getCount(),
                'name': iw,
                'path': w[iw].get('path', ''),
                'type': w[iw].get('type', '')
              }
    return {'cnt_domains': 0, 
            'cnt_tags': 0, 
            'cnt_services': 0,
            'cnt_links': 0,
            'name': '',
            'path': '',
            'type': ''
             }

  def getDomains(self, iw):
    if self.exists(iw):
      return self.m[iw]['domains']
    return Domains()

  def getTags(self, iw):
    if self.exists(iw):
      return self.m[iw]['tags']
    return Tags()

  def getServices(self, iw):
    if self.exists(iw):
      return self.m[iw]['services']
    return Services()

  def getLinks(self, iw):
    if self.exists(iw):
      return self.m[iw]['links']
    return Links()

  def filterTag(self, iw, name, tag):
    if not self.exists(iw):
      return Domains(), Services(), Links()
      
    srv = self.m[iw]['services'].filter('tags', tag)
    services = Services()
    services.set(srv)
    
    lsrv = services.getVariants('id')
    
    srvlinks = Links()
    #linksFrom = self.srvlinks.filter('service_from', lsrv)
    #srvlinks.set(linksFrom)
    #linksTo = self.srvlinks.filter('service_to', lsrv)
    #srvlinks.append(linksTo)
    
    links = self.m[iw]['links'].filter('tags', tag)
    srvlinks.set(links)
    #srvlinks.append(links)
    #links = self.srvlinks.filter('service_from', lsrv)
    #srvlinks.append(links)
    
    srvsTo = srvlinks.getVariants('item_to')
    srvs1 = self.services.filter('id', srvsTo)
    services.append(srvs1)
    
    srvsFrom = srvlinks.getVariants('item_from')
    srvs1 = self.services.filter('id', srvsFrom)
    services.append(srvs1)

    ldmn = services.getVariants('domain')
    domains = self.m[iw]['domains'].filter('id', ldmn)
    
    return domains, services.get(), srvlinks.get()
