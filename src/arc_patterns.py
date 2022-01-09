#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import git
from pathlib import Path
import pylightxl as xl

from urllib.parse import urlencode, quote
from pprint import pprint
from datetime import date

from .obj.domains import Domains
from .obj.services import Services
from .obj.api import API
from .obj.links import Links
from .obj.tags import Tags
from .obj.elog import ELog
from .fabricdia import FabricDia
from .fs import FS
from .html import HTML

import re


class ArcPatterns():
  def __init__ (self, fs, config, verbose):
    self.fs = fs

    self.verbose = verbose
    self.domains = Domains()
    self.api = API()
    self.services = Services()
    self.links = Links()
    self.tags = Tags()

    self.html = HTML(self.fs, verbose)
    self.dia = FabricDia(self.fs, self.html, config, verbose)

  def update(self):
    pathname = "%s/arc.patterns" % self.fs.getPathTempDir()
    try:
      if self.verbose > 5:
        print("DBG: GIT clone/pull patterns %s" % (pathname))
      if not os.path.exists(pathname):
        git.Repo.clone_from('https://github.com/Lunkov/arc.patterns.git', pathname, branch='master')
      else:
        repo = git.Repo(pathname)
        repo.git.checkout('master')
        repo.remotes[0].pull()
    
    except Exception as err:
      print("FATAL: GIT Clone(%s): %s" % (pathname, str(err)))
    self.readXLSs(pathname)
    
  def readXLSs(self, pathname):
    fp = os.path.abspath(pathname)
    fullPath = fp
    if self.verbose:
      print("LOG: XLSs read from '%s'..." % fp)
    try:
      for path in Path(fp).rglob('*.xlsx'):
        fullPath = os.path.join(fp, path.parent, path.name)
        if os.path.isfile(fullPath):
          self.readXLS(fullPath)
          
    except Exception as err:
      print("FATAL: File(%s): %s" % (fullPath, str(err)))
    
  def readXLS(self, filename):
    if self.verbose:
      print("LOG: Reading '%s'..." % filename)
    try:
      db = xl.readxl(fn=filename)
      self.domains.readXLS(db, 'DOMAINS')
      self.services.readXLS(db, 'SERVICES')
      self.links.readXLS(db, 'LINKS')
      self.tags.readXLS(db, 'TAGS')
      if self.verbose:
        print("LOG: Read '%s' - OK" % filename)
    except Exception as err:
      print("FATAL: File(%s): %s" % (filename, str(err)))

  def filterTag(self, name, tag):
    srv = self.services.filter('tags', tag)
    services = Services()
    services.set(srv)
    
    lsrv = services.getVariants('id')
    
    srvlinks = Links()
    #linksFrom = self.srvlinks.filter('service_from', lsrv)
    #srvlinks.set(linksFrom)
    #linksTo = self.srvlinks.filter('service_to', lsrv)
    #srvlinks.append(linksTo)
    
    links = self.links.filter('tags', tag)
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
    domains = self.domains.filter('id', ldmn)
    
    return domains, services.get(), srvlinks.get()
    
  def makeAll(self):
    self.cnt_files = 0
    self.cnt_writes = 0
    
    htmlPath = self.fs.getPathHTML()

    elog = ELog()
    if self.verbose:
      print("LOG: Rebuilding HTML...")

    if self.verbose:
      print("LOG: Syncing HTML...")
    
    self.fs.mkDir(htmlPath + '/%s',
                   ['dia', 'patterns', 'patterns/tag'])

    #self.html.render('legend.html',      '%s/patterns/legend.html' % htmlPath, {'domains': self.domains.getItems(), 'services': self.services.getItems(), 'tags': self.tags.getItems()})
    #self.html.render('arcpatterns.html', '%s/patterns/tags.html'   % htmlPath, {'tags': self.tags.getItems(), 'services': self.services.getItems()})

    self.dia.drawBlockDiagramLegend('legend', '%s/dia/legend' % (htmlPath))

    '''
    if self.verbose:
      print("LOG: Rebuilding HTML for Tags (%d)..." % self.tags.getCount())
    for j, tag in self.tags.getItems():
      domains, services, srvlinks = self.filterTag(j, j)
      self.dia.drawBlockDiagram(j, domains, services, srvlinks, '%s/dia/tag/%s' % (htmlPath, j.replace('/', '-')))
      self.html.render('arcpattern.html', '%s/patterns/tag/%s.html' % (htmlPath, j),
                        {'tag': tag,
                         'fsd': [],
                         'tag_servicelinks': srvlinks.items(),
                         'tag_services': services.items()})
    
    self.fs.printStats()
    
    '''
