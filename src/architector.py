#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import logging
import os
import yaml
from csv import reader
import pylightxl as xl
from urllib.parse import urlencode, quote
from pprint import pprint
from datetime import date

from .domains import Domains
from .services import Services
from .api import API
from .links import Links
from .tags import Tags
from .servicelinks import ServiceLinks
from .mermaid import Mermaid
from .elog import ELog

import re
import hashlib
import jinja2
import sysrsync

import graphviz
import networkx as nx
from netwulf import visualize
from pyvis.network import Network
from diagrams import Diagram



class Architector():
  def __init__ (self, verbose):
    self.verbose = verbose;
    self.domains = Domains()
    self.api = API()
    self.services = Services(self.api)
    self.srvlinks = ServiceLinks()
    self.links = Links()
    self.tags = Tags()
    
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
  
  def loadDesign(self, p):
    for path, subdirs, files in os.walk(p):
      for name in files:
        if not os.path.isfile(os.path.join(path, name)):
          continue
        if '.seq' in name:
          filename = os.path.join(path, name)
          data, ok = self.parseDesign(filename)
          if ok:
            pprint(data)

  def parseDesign(self, filename):
    data = {}
    ok = False
    try:
      f = open(filename, 'r')
      content = f.read()
      f.close()
      data = yaml.safe_load(content)
      ok = True
    except Exception as e:
      print("ERR: File read '%s': %s" % (filename, str(e)))
    return data, ok

  def nowDate(self):
    today = date.today()
    return today.strftime("%Y-%m-%d")
  
  def readXLS(self, filename):
    if self.verbose:
      print("LOG: Reading '%s'..." % filename)
    db = xl.readxl(fn=filename)
    self.domains.readXLS(db, 'DOMAINS')
    self.services.readXLS(db, 'SERVICES')
    self.srvlinks.readXLS(db, 'SERVICE.LINKS')
    self.api.readXLS(db, 'API')
    self.links.readXLS(db, 'SEQUENCES')
    self.tags.readXLS(db, 'TAGS')
    self.srvlinks.calc(self.services)
    if self.verbose:
      print("LOG: Read '%s' - OK" % filename)
    
  def updateOnlineData(self):
    if self.verbose:
      print("LOG: Updating online data...")
    self.services.updateSwaggerAll(self.nowDate())
    if self.verbose:
      print("LOG: Update online data - OK")

  def writeXLS(self, filename):
    db = xl.Database()
    self.domains.writeXLS(db, 'DOMAINS')
    self.services.writeXLS(db, 'SERVICES')
    self.srvlinks.writeXLS(db, 'SERVICE.LINKS')
    self.api.writeXLS(db, 'API')
    self.links.writeXLS(db, 'LINKS')
    self.tags.writeXLS(db, 'TAGS')
    xl.writexl(db = db, fn = filename % (self.nowDate()))

  def dump(self):
    self.domains.dumpCSV('data/domains.csv')
    self.services.dumpCSV('data/services.csv')
    self.api.dumpCSV('data/api.csv')
    
  def graphWULF(self):
    G = nx.Graph()
    labels = {}
    self.domains.graphWULF(G, labels)
    self.services.graphWULF(G)
    self.api.graphWULF(G)
    # visualize(G)
    graph = nx.drawing.nx_pydot.to_pydot(G)
    output_raw_dot = graph.to_string()
    graph.write_raw('out/schema.dot')    
    graph.write_png('out/schema.png')

  def graphVIZ(self):
    G = Network()
    self.domains.graphVIZ(G)
    self.services.graphVIZ(G)
    self.api.graphVIZ(G)
    self.links.graphVIZ(G)
    
    G.show_buttons(filter_=['physics'])
    # G.enable_physics(True)
    G.show('mygraph.html')

  def buldPage(self, name):
    html = open("templates/%s.html" % name).read()
    template = Template(html)
    html = HTML()
    html.save(name, template.render({'domains': self.domains.getItems(), 'services': self.services.getItems(), }))

  def graphDia(self):
    for i, service in self.services.getItems():
      D = Diagram(i, show=False)
      self.service.graphDia(D, i)

  def graph(self):
    D = Mermaid()
    D.new('flowLR', 'all')

    for j, domain in self.domains.getItems():
      self.domains.graph(D, domain)
      
    for i, service in self.services.getItems():
      self.services.graph(D, service)

    for i, link in self.srvlinks.getItems():
      self.srvlinks.graph(D, link)

    return D.finish()

  def graphTag(self, tag):
    D = Mermaid()
    D.new('flowLR', tag)
    
    srv = self.services.filter('tags', tag)
    services = Services(self.api)
    services.set(srv)
    
    lsrv = services.getVariants('id')
    
    srvlinks = ServiceLinks()
    linksFrom = self.srvlinks.filter('service_from', lsrv)
    srvlinks.set(linksFrom)
    linksTo = self.srvlinks.filter('service_to', lsrv)
    srvlinks.append(linksTo)
    
    links = srvlinks.filter('tags', tag)
    srvlinks.set(links)
    
    srvsTo = srvlinks.getVariants('service_to')
    srvs1 = self.services.filter('id', srvsTo)
    services.append(srvs1)
    
    srvsFrom = srvlinks.getVariants('service_from')
    srvs1 = self.services.filter('id', srvsFrom)
    services.append(srvs1)

    ldmn = services.getVariants('domain')
    domains = self.domains.filter('id', ldmn)
    
    
    for j, domain in domains.items():
      self.domains.graph(D, domain)
      
    for i, service in services.getItems():
      services.graph(D, service)

    for i, link in srvlinks.getItems():
      srvlinks.graph(D, link)

    return D.finish()

  def graphService(self, service):
    D = Mermaid()
    D.new('flowLR', service)
    
    srv = self.services.filter('id', service)
    services = Services(self.api)
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
    
    
    for j, domain in domains.items():
      self.domains.graph(D, domain)
      
    for i, service in services.getItems():
      services.graph(D, service)

    for i, link in srvlinks.getItems():
      srvlinks.graph(D, link)

    return D.finish()

  def graphDomain(self, domain):
    D = Mermaid()
    D.new('flowLR', domain)
    
    srv = self.services.filter('domain', domain)
    services = Services(self.api)
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
    
    for j, domain in domains.items():
      self.domains.graph(D, domain)
      
    for i, service in services.getItems():
      services.graph(D, service)

    for i, link in srvlinks.getItems():
      srvlinks.graph(D, link)

    return D.finish()

  def makeAll(self, htmlPath):
    elog = ELog()
    if self.verbose:
      print("LOG: Rebuilding HTML...")

    if self.verbose:
      print("LOG: Syncing HTML...")
    for p in ['data', 'service', 'domain', 'tag', 'dia', 'dia/service', 'dia/tag', 'dia/domain', 'swagger', 'api']:
      os.makedirs('%s/%s' % (htmlPath, p), exist_ok=True)

    for p in ['js', 'css', 'img', 'scss', 'vendor']:
      if os.name != 'nt':
        sysrsync.run(source = 'templates/%s' % p,
                   destination = '%s/%s' % (htmlPath, p),
                   sync_source_contents = True,
                   exclusions = ['.~*', 'Thumbs.db:encryptable'],
                   options = ['-a'],
                   verbose = self.verbose)

    self.htmlRender('index.html',    '%s/index.html'    % htmlPath)
    self.htmlRender('domains.html',  '%s/domains.html'  % htmlPath)
    self.htmlRender('services.html', '%s/services.html' % htmlPath)
    self.htmlRender('tags.html',     '%s/tags.html'     % htmlPath)
    self.htmlRender('apis.html',     '%s/apis.html'     % htmlPath, prop = {'api': self.api.getItems()})
    self.htmlRender('errors.html',   '%s/errors.html'   % htmlPath, prop = {'errors': elog.getItems()})

    self.tags.writeJSON('%s/data/tags.json'          % htmlPath)
    self.domains.writeJSON('%s/data/domains.json'    % htmlPath)
    self.services.writeJSON('%s/data/services.json'  % htmlPath)

    text = self.graph()
    text_file = codecs.open('%s/dia/index.html' % htmlPath, 'w', 'utf-8')
    text_file.write(text)
    text_file.close()

    if self.verbose:
      print("LOG: Rebuilding HTML for Domains (%d)..." % self.domains.getCount())
    for j, domain in self.domains.getItems():
      text = self.graphDomain(j)
      text_file = codecs.open('%s/dia/domain/%s.html' % (htmlPath, j.replace('/', '-')), 'w', 'utf-8')
      text_file.write(text)
      text_file.close()
      domain_services = self.services.filter('domain', j)    
      self.htmlRender('domain.html', '%s/domain/%s.html' % (htmlPath, j),
                       prop = {'domain': domain,
                               'domain_services': domain_services.items()})

    if self.verbose:
      print("LOG: Rebuilding HTML for Tags (%d)..." % self.tags.getCount())
    for j, tag in self.tags.getItems():
      text = self.graphTag(j)
      text_file = codecs.open('%s/dia/tag/%s.html' % (htmlPath, j), 'w', 'utf-8')
      text_file.write(text)
      text_file.close()
      tag_services = self.services.filter('tags', j)    
      self.htmlRender('tag.html', '%s/tag/%s.html' % (htmlPath, j),
                       prop = {'tag': tag,
                               'tag_services': tag_services.items()})

    if self.verbose:
      print("LOG: Rebuilding HTML for Services (%d)..." % self.services.getCount())
    for j, service in self.services.getItems():
      text = self.graphService(j)
      text_file = codecs.open('%s/dia/service/%s.html' % (htmlPath, j.replace('/', '-')), 'w', 'utf-8')
      text_file.write(text)
      text_file.close()
      linksFrom = self.srvlinks.filter('service_from', j)
      linksTo = self.srvlinks.filter('service_to', j)
      service_api = self.api.filter('service', j)
      self.htmlRender('service.html', '%s/service/%s.html' % (htmlPath, j.replace('/', '-')),
                       prop = {'service': service,
                               'service_api': service_api.items(),
                               'links_from': linksFrom.items(),
                               'links_to': linksTo.items()})

    if self.verbose:
      print("LOG: Rebuilding HTML for APIs (%d)..." % self.api.getCount())
    for j, api in self.api.getItems():
      self.htmlRender('api.html', '%s/api/%s.html' % (htmlPath, api.get('linkin', 'undef')),
                       prop = {'api': api})

    if self.verbose:
      print("LOG: Rebuild HTML - OK")

  def htmlRender(self, tmplfile, dstfile, prop = {}):
    #text = self.graph()
    
    templateLoader = jinja2.FileSystemLoader(searchpath="./templates/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(tmplfile)
    outputText = template.render(domains = self.domains.getItems(), tags = self.tags.getItems(), services = self.services.getItems(), prop = prop) #, schema = text)
    text_file = codecs.open(dstfile, 'w', 'utf-8')
    text_file.write(outputText)
    text_file.close()
