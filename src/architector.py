#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path
import pylightxl as xl

from urllib.parse import urlencode, quote
from pprint import pprint
from datetime import date

from .domains import Domains
from .services import Services
from .api import API
from .links import Links
from .tags import Tags
from .fsd import FSD
from .swaggers import Swaggers
from .structs import Structs
from .update import Updates
from .uploader import Uploader
from .servicelinks import ServiceLinks
from .fabricdia import FabricDia
from .elog import ELog
from .fs import FS
from .html import HTML

import re


class Architector():
  def __init__ (self, fs, verbose):
    self.fs = fs

    self.verbose = verbose
    self.domains = Domains()
    self.api = API()
    self.services = Services()
    self.srvlinks = ServiceLinks()
    self.links = Links()
    self.tags = Tags()
    self.fsd = FSD()
    self.swaggers = Swaggers(verbose)
    self.structs = Structs()
    self.updates = Updates(verbose)

    self.html = HTML(self.fs, verbose)
    self.dia = FabricDia(self.fs, self.html, verbose)

  def loadServices(self, fileServices):
    columns = {}
    i = 0
    with codecs.open(fileServices, 'r', 'utf_8_sig') as read_obj:
      csv_reader = reader(read_obj)
      for row in csv_reader:
        i = i + 1
        if i == 1:
          j = 0
          for col in row:
            columns[col] = j
            j = j + 1
          continue

        self.domains.add(row[columns['place']], {'name': row[columns['place']]})
        self.services.add(row[columns['name']], {'name': row[columns['name']], 'domain': row[columns['place']], 'description': row[columns['description']], 'link': row[columns['link']], 'swagger': row[columns['swagger']]})
        self.services.reloadSwagger(row[columns['name']], self.api)
  
  def nowDate(self):
    today = date.today()
    return today.strftime("%Y-%m-%d")
  
  def loadData(self):
    self.swaggers.load(os.path.join(self.fs.getPathData(), 'swaggers'))
    for i, sw in self.swaggers.getItems():
      if not 'swagger-data' in sw:
        print("ERR: Swagger data '%s' Not found struct" % (i))
        continue
      if not 'info' in sw['swagger-data']:
        continue
      description = ''
      service = ''
      version = ''
      if 'description' in sw['swagger-data']['info']:
        description = sw['swagger-data']['info']['description']
      if 'title' in sw['swagger-data']['info']:
        service = sw['swagger-data']['info']['title']
      if 'version' in sw['swagger-data']['info']:
        version = sw['swagger-data']['info']['version']
      for path, va in  sw['swagger-data']['paths'].items():
        for method, vm in  va.items():
          desc = description
          if 'description' in vm:
            desc = vm['description']
          ida = service + '.' + version + '.' + method.upper() + '.' + path
          title = method.upper() + ' ' + path
          self.api.addItem(ida, { 'id': ida, 'title': title, 'service': service, 'version': version, 'status': 'fact', 'method': method.upper(), 'url': path, 'description': desc} )

    self.updates.load(os.path.join(self.fs.getPathData(), 'updates'))
    self.updates.calc(self.services)
    res = self.updates.makeSwaggers()
    for i, sw in res.items():
      if not 'info' in sw:
        continue
      description = ''
      service = ''
      version = ''
      if 'description' in sw['info']:
        description = sw['info']['description']
      if 'title' in sw['info']:
        service = sw['info']['title']
      if 'version' in sw['info']:
        version = sw['info']['version']
      for path, va in  sw['paths'].items():
        for method, vm in  va.items():
          desc = description
          if 'description' in vm:
            desc = vm['description']
          ida = service + '.' + version + '.' + method.upper() + '.' + path
          title = method.upper() + ' ' + path
          self.api.addItem(ida, { 'id': ida, 'title': title, 'service': service, 'version': version, 'status': 'plan', 'method': method.upper(), 'url': path, 'description': desc} )


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
    db = xl.readxl(fn=filename)
    self.domains.readXLS(db, 'DOMAINS')
    self.fsd.readXLS(db, 'FSD')
    self.services.readXLS(db, 'SERVICES')
    self.srvlinks.readXLS(db, 'SERVICE.LINKS')
    self.api.readXLS(db, 'API')
    self.tags.readXLS(db, 'TAGS')
    if self.verbose:
      print("LOG: Read '%s' - OK" % filename)

  def analyze(self):
    srv = Services()
    for j, fsd in self.fsd.getItems():
      fsd_services = self.services.filter('tags', fsd.get('tags', ''))
      srv.set(fsd_services)
      self.fsd.m[j]['services'] = srv.getVariants('id')
    
  def updateOnlineData(self):
    if self.verbose:
      print("LOG: Updating online data...")
    uploader = Uploader(self.fs, '%s/swaggers' % self.fs.getPathData(), self.verbose)
    for i, service in self.services.getItems():
      if 'swagger' in service:
        uploader.updateSwagger(service)
  
  def prepare(self):
    self.srvlinks.calc(self.services)
    for i, service in self.services.getItems():
      service_swaggers = self.swaggers.filter('service', i)
      if len(service_swaggers) > 1:
        print("WRN: Service '%s' have %d swaggers" % (i, len(service_swaggers)))
        for isw, swg in service_swaggers.items():
          #print("WRN: Service '%s' have %s" % (isw, swg))
          print("WRN: Service '%s' have" % (isw))
        #pprint(service_swaggers)

    for i, swagger in self.swaggers.getItems():
      if 'swagger-data' in swagger:
        if 'components' in swagger['swagger-data']:
          if 'schemas' in swagger['swagger-data']['components']:
            for j, st in swagger['swagger-data']['components']['schemas'].items():
              key = "%s.%s.%s" % (swagger.get('service', ''), swagger.get('version', ''), j)
              p = {}
              if 'properties' in st:
                p = st['properties']
                
              self.structs.addItem(key, {'description': st.get('description', ''),
                                         'type': st.get('type', ''),
                                         'name': j,
                                         'properties': p,
                                         'service': swagger.get('service', ''),
                                         'service.version': "%s.%s" % (swagger.get('service', ''), swagger.get('version', ''))
                                        })

    if self.verbose:
      print("LOG: Update online data - OK")

  def writeXLS(self, filename):
    db = xl.Database()
    self.domains.writeXLS(db, 'DOMAINS')
    self.services.writeXLS(db, 'SERVICES')
    self.fsd.writeXLS(db, 'FSD')
    self.srvlinks.writeXLS(db, 'SERVICE.LINKS')
    self.api.writeXLS(db, 'API')
    self.links.writeXLS(db, 'LINKS')
    self.tags.writeXLS(db, 'TAGS')
    xl.writexl(db = db, fn = filename % (self.nowDate()))

  def dump(self):
    self.domains.dumpCSV('data/domains.csv')
    self.services.dumpCSV('data/services.csv')
    self.api.dumpCSV('data/api.csv')

  def filterTag(self, name, tag):
    srv = self.services.filter('tags', tag)
    services = Services()
    services.set(srv)
    
    lsrv = services.getVariants('id')
    
    srvlinks = ServiceLinks()
    #linksFrom = self.srvlinks.filter('service_from', lsrv)
    #srvlinks.set(linksFrom)
    #linksTo = self.srvlinks.filter('service_to', lsrv)
    #srvlinks.append(linksTo)
    
    links = self.srvlinks.filter('tags', tag)
    srvlinks.set(links)
    #srvlinks.append(links)
    #links = self.srvlinks.filter('service_from', lsrv)
    #srvlinks.append(links)
    
    srvsTo = srvlinks.getVariants('service_to')
    srvs1 = self.services.filter('id', srvsTo)
    services.append(srvs1)
    
    srvsFrom = srvlinks.getVariants('service_from')
    srvs1 = self.services.filter('id', srvsFrom)
    services.append(srvs1)

    ldmn = services.getVariants('domain')
    domains = self.domains.filter('id', ldmn)
    
    return domains, services.get(), srvlinks.get()
    
  def findSources(self, srvlinks, service_from):
    linksFrom = self.srvlinks.filter('service_from', service_from)
    if len(linksFrom) > 0:
      srvlinks.append(linksFrom)
      linkstmp = ServiceLinks()
      linkstmp.set(linksFrom)
      service_to = linkstmp.getVariants('service_to')
      self.findSources(srvlinks, service_to)
  
  def filterService(self, name, service):
    srv = self.services.filter('id', service)
    services = Services()
    services.set(srv)
    
    srvlinks = ServiceLinks()
    linksFrom = self.srvlinks.filter('service_from', service)
    srvlinks.set(linksFrom)
    linksTo = self.srvlinks.filter('service_to', service)
    srvlinks.append(linksTo)
    
    srvsTo = srvlinks.getVariants('service_to')
    srvs1 = self.services.filter('id', srvsTo)
    services.append(srvs1)
    
    srvsFrom = srvlinks.getVariants('service_from')
    srvs1 = self.services.filter('id', srvsFrom)
    services.append(srvs1)

    ldmn = services.getVariants('domain')
    domains = self.domains.filter('id', ldmn)
    
    srvsIds = services.getVariants('id')
    
    return domains, services.get(), srvlinks.get(), self.updates.filter('service', srvsIds)

  def filterDomain(self, domain):
    srv = self.services.filter('domain', domain)
    services = Services()
    services.set(srv)
    srvs = services.getVariants('id')
    
    srvlinks = ServiceLinks()
    linksFrom = self.srvlinks.filter('service_from', srvs)
    srvlinks.set(linksFrom)
    linksTo = self.srvlinks.filter('service_to', srvs)
    srvlinks.append(linksTo)
    
    srvsTo = srvlinks.getVariants('service_to')
    srvs1 = self.services.filter('id', srvsTo)
    services.append(srvs1)
    
    srvsFrom = srvlinks.getVariants('service_from')
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
                   ['data', 'service', 'domain', 'tag', 'fsd',
                    'up', 'dia', 'swagger', 'api',
                    'dia/service', 'dia/tag', 'dia/up', 'dia/fsd', 'dia/domain'])

    self.fs.rsync(self.fs.getPathTemplates() + '/%s', htmlPath + '/%s', ['js', 'css', 'scss', 'vendor'])
    self.fs.rsync(self.fs.getPathData() + '/%s', htmlPath + '/%s', ['updates', 'swaggers'])

    self.html.render('legend.html',   '%s/legend.html'   % htmlPath, {'domains': self.domains.getItems(), 'services': self.services.getItems(), 'tags': self.tags.getItems()})
    self.html.render('index.html',    '%s/index.html'    % htmlPath, {'domains': self.domains.getItems(), 'services': self.services.getItems(), 'tags': self.tags.getItems()})
    self.html.render('domains.html',  '%s/domains.html'  % htmlPath, {'domains': self.domains.getItems()})
    self.html.render('services.html', '%s/services.html' % htmlPath, {'services': self.services.getItems()})
    self.html.render('tags.html',     '%s/tags.html'     % htmlPath, {'tags': self.tags.getItems(), 'services': self.services.getItems()})
    self.html.render('fsds.html',     '%s/fsds.html'     % htmlPath, {'fsds': self.fsd.getItems()})
    self.html.render('apis.html',     '%s/apis.html'     % htmlPath, {'apis': self.api.getItems(), 'services': self.services.getItems()})
    self.html.render('errors.html',   '%s/errors.html'   % htmlPath, {'errors': elog.getItems()})

    self.tags.writeJSON('%s/data/tags.json'          % htmlPath)
    self.domains.writeJSON('%s/data/domains.json'    % htmlPath)
    self.services.writeJSON('%s/data/services.json'  % htmlPath)
    self.updates.writeJSON('%s/data/updates.json'    % htmlPath)

    self.dia.drawBlockDiagram('index', self.domains.get(), self.services.get(), self.srvlinks.get(), '%s/dia/index' % (htmlPath))
    self.dia.drawBlockDiagramLegend('legend', '%s/dia/legend' % (htmlPath))

    if self.verbose:
      print("LOG: Rebuilding HTML for Domains (%d)..." % self.domains.getCount())
    for j, domain in self.domains.getItems():
      domains, services, srvlinks = self.filterDomain(j)
      self.dia.drawBlockDiagram(j, domains, services, srvlinks, '%s/dia/domain/%s' % (htmlPath, j.replace('/', '-')))
      self.html.render('domain.html', '%s/domain/%s.html' % (htmlPath, j),
                        {'domain': domain,
                         'domains': domains,
                         'domain_servicelinks': srvlinks.items(),
                         'domain_services': services.items()})

    if self.verbose:
      print("LOG: Rebuilding HTML for Tags (%d)..." % self.tags.getCount())
    for j, tag in self.tags.getItems():
      domains, services, srvlinks = self.filterTag(j, j)
      self.dia.drawBlockDiagram(j, domains, services, srvlinks, '%s/dia/tag/%s' % (htmlPath, j.replace('/', '-')))
      tag_fsd = self.fsd.filter('tags', j)
      self.html.render('tag.html', '%s/tag/%s.html' % (htmlPath, j),
                        {'tag': tag,
                         'fsd': tag_fsd.items(),
                         'tag_servicelinks': srvlinks.items(),
                         'tag_services': services.items()})

    if self.verbose:
      print("LOG: Rebuilding HTML for Services (%d)..." % self.services.getCount())
    for j, service in self.services.getItems():
      domains, services, srvlinks, ups = self.filterService(j, j)
      self.dia.drawBlockDiagram(j, domains, services, srvlinks, '%s/dia/service/%s' % (htmlPath, j.replace('/', '.')))

      linksFrom = self.srvlinks.filter('service_from', j)
      linksTo = self.srvlinks.filter('service_to', j)
      service_api = self.api.filter('service', j)
      service_fsd = self.fsd.filter('services', j)
      service_ups = self.updates.filter('service', j)
      service_swaggers = self.swaggers.filter('service', j)
      self.html.render('service.html', '%s/service/%s.html' % (htmlPath, j.replace('/', '-')),
                        {'service': service,
                         'ups': service_ups.items(),
                         'fsd': service_fsd.items(),
                         'swaggers': service_swaggers.items(),
                         'service_api': service_api.items(),
                         'links_from': linksFrom.items(),
                         'links_to': linksTo.items()})

    if self.verbose:
      print("LOG: Rebuilding HTML for APIs (%d)..." % self.api.getCount())
    for j, api in self.api.getItems():
      self.html.render('api.html', '%s/api/%s.html' % (htmlPath, api.get('linkin', 'undef')),
                       prop = {'api': api})

    if self.verbose:
      print("LOG: Rebuilding HTML for FSDs (%d)..." % self.fsd.getCount())
    
    for j, fsd in self.fsd.getItems():
      domains, services, srvlinks = self.filterTag(j, fsd.get('tags', ''))
      self.dia.drawBlockDiagram(j, domains, services, srvlinks, '%s/dia/fsd/%s' % (htmlPath, j))
      self.html.render('fsd.html', '%s/fsd/%s.html' % (htmlPath, j),
                       {'fsd': fsd,
                        'fsd_servicelinks': srvlinks.items(),
                        'fsd_services': services.items()})

    if self.verbose:
      print("LOG: Rebuilding HTML for Swaggers (%d)..." % self.swaggers.getCount())
    self.html.render('swaggers.html', '%s/swaggers.html'     % htmlPath, {'swaggers': self.swaggers.getItems()})
    for j, swagger in self.swaggers.getItems():
      sts = self.structs.filter('service.version', "%s.%s" % (swagger.get('service', ''), swagger.get('version', '')))
      stn = {}
      for i, st in sts.items():
        stn[st['name']] = st
      swaggerurl = ''
      sr = self.services.getItem(swagger.get('service', ''))
      if not None is sr:
        if 'swagger' in sr:
          swaggerurl = sr['swagger']
      self.html.render('swagger.html', '%s/swagger/%s.html' % (htmlPath, j),
                       {'swaggerinfo': swagger,
                        'swaggerurl': swaggerurl,
                        'swagger': swagger['swagger-data'],
                        'structs': stn})

    if self.verbose:
      print("LOG: Rebuilding HTML for Updates (%d)..." % self.updates.getCount())
    self.html.render('ups.html',      '%s/ups.html'      % htmlPath, {'ups': self.updates.getItems()})
    
    if self.verbose:
      print("LOG: Rebuild HTML - OK")

    for j, up in self.updates.getItems():
      text = self.dia.drawSequenceDiagram(j, up, self.services.get(), '%s/dia/up/%s' % (htmlPath, j))
      self.html.render('up.html', '%s/up/%s.html' % (htmlPath, j),
                       {'up': up})
    
    self.fs.printStats()
    

