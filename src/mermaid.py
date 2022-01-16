#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import logging
import os

from urllib.parse import urlencode, quote
from pprint import pprint
from datetime import date

import hashlib

class Mermaid():
  def __init__ (self, config):
    self.tab = '    '
    self.typeDia = ''

    self.gNodes = {}
    self.gGroups = {}
    self.gLinks = {}
    
    print('===')
    pprint(config)
    print('===')

    self.typeNodesDef = '["%s"]'
    self.typeNodes = {}
    if 'objects' in config:
      self.typeNodes = config['objects']
    self.statusNodes = {}
    if 'objects-status' in config:
      self.statusNodes = config['objects-status']

    self.typeLinksDefault = '-...-|%s|'
    self.typeLinks = {}
    if 'links' in config:
      self.typeLinks = config['links']
    self.statusLinks = {}
    if 'links-status' in config:
      self.statusLinks = config['links-status']

    self.typeSeqLinksDefault = '->>'
    self.typeSeqLinks = {}
    if 'links' in config:
      self.typeSeqLinks = config['links']


  def new(self, typeDia, name):
    self.name = name
    self.typeDia = typeDia
    self.gGroups = {}
    self.gNodes = {}
    self.gLinks = {}

  def makeLegend(self, name):
    self.new('flowLR', name)
    
    self.group('status', 'Status of nodes')
    for i, v in self.statusNodes.items():
      if i == 'undef':
        self.node(i, i, 'status', 'service', '-', '', i)
      else:
        self.node(i, i, 'status', 'service', i, '', i)

    ki = 0
    kc = int(len(self.typeNodes) / 5)
    self.group('type%d' % kc, 'Types of nodes %d' % kc)
    for i, v in self.typeNodes.items():
      ki = ki + 1
      self.node(i, i, ('type%d' % kc), i, 'ok', '', i)
      if ki % 5 == 0:
        kc = kc - 1
        self.group('type%d' % kc, 'Types of nodes %d' % kc)

    self.group('typelinks', 'Types of links')
    for i, v in self.typeLinks.items():
      idn1 = hashlib.md5((i+'-srv1').encode('utf-8')).hexdigest()
      idn2 = hashlib.md5((i+'-srv2').encode('utf-8')).hexdigest()
      self.node(idn1, 'Service 1', 'typelinks', 'service', 'ok', '', i)
      self.node(idn2, 'Service 2', 'typelinks', 'service', 'ok', '', i)
      self.link(idn1, idn2, 'typelinks', '', i, i)

    return self.finish()

  def _node(self, id, name, ntype = '', description = ''):
    idn = hashlib.md5(id.encode('utf-8')).hexdigest()
    nname = name.replace('"', '\'').replace('(', ' ').replace(')', ' ') #.replace(':', '\:').replace('.', '\.')
    ndescription = description.replace('"', '\'').replace(':', '\:').replace('.', '\.')
    N = ''
    if ntype in self.typeNodes:
      N = self.typeNodes[ntype].get('view', '[%s]') % (nname)
    else:
      N = self.typeNodesDef % (nname)
    return idn, ("%s%s%s\n" % (self.tab, idn, N))    

  def node(self, id, name, group = '-', ntype = '', status = '', link = '', description = ''):
    if not group in self.gNodes:
      self.gNodes[group] = ''
    G = self.gNodes[group]
    idn, N = self._node(id, name, ntype, description)
    
    G = G + N
    
    if status in self.statusNodes:
      G = G + ("%sstyle %s %s;\n" % (self.tab, idn, self.statusNodes[status]))
    #else:
    #  G = G + ("%sstyle %s %s;\n" % (self.tab, idn, self.statusNodes['undef']))

    if link != '':
      # COMMENT: For HTTP ref => G = G + ("%sclick %s \"%s\" _blank\n" % (self.tab, idn, link))
      G = G + ("%sclick %s call nodeClick(\"%s\")\n" % (self.tab, idn, id))
    self.gNodes[group] = G

  def group(self, id, name, status = '', link = ''):
    if not id in self.gGroups:
      self.gGroups[id] = ''
    G = self.gGroups[id]
    
    idn = hashlib.md5(('group:'+id).encode('utf-8')).hexdigest()
    G = G + ("%ssubgraph %s[\"%s\"]\n" % (self.tab, idn, name.replace('"', '\'')))

    # TODO
    #if link != "":
    #  G = G + ("%sclick %s \"%s\" _blank\n" % (self.tab, idn, link))

    self.gGroups[id] = G

  def link(self, service_from, service_to, group = '-', tags = '', status = '', text = ''):
    if not group in self.gNodes:
      self.gNodes[group] = ''
    
    G = self.gNodes[group]

    idn1 = hashlib.md5(service_from.encode('utf-8')).hexdigest()
    idn2 = hashlib.md5(service_to.encode('utf-8')).hexdigest()
    linktext = ''
    if len(text) > 0:
      linktext = text.replace('"', '\'')
    
    N = ''
    
    if status in self.typeLinks:
      N = self.typeLinks[status].get('view', '-- %s --') % linktext
    else:
      print('WRN: status not found "%s"' % status)
      N = self.typeLinksDefault % linktext
    N = N.replace('||', '')
    G = G + ("%s%s %s %s\n" % (self.tab, idn1, N, idn2))
    #if status in self.statusLinks:
    #  G = G + ("%sstyle %s %s;\n" % (self.tab, idn1, self.statusLinks[status]))

    self.gNodes[group] = G

  def sequenceNote(self, group, service, text = ''):
    if text == '':
      return
    if not group in self.gLinks:
      self.gLinks[group] = ''

    idn = hashlib.md5(service.encode('utf-8')).hexdigest()
    G = self.gLinks[group]
    G = G + ("%sNote right of %s: %s\n" % (self.tab, idn, text))
    self.gLinks[group] = G

  def sequence(self, group, service_from, service_to, api = '', ntype = ''):

    idn1 = hashlib.md5(service_from.encode('utf-8')).hexdigest()
    idn2 = hashlib.md5(service_to.encode('utf-8')).hexdigest()

    if not idn1 in self.gNodes:
      self.gNodes[idn1] = '%sparticipant %s as %s\n' % (self.tab, idn1, service_from)
    if not idn2 in self.gNodes:
      self.gNodes[idn2] = '%sparticipant %s as %s\n' % (self.tab, idn2, service_to)
    
    if not group in self.gLinks:
      self.gLinks[group] = ''

    G = self.gLinks[group]

    linktext = ''
    if api and len(api) > 0:
      linktext = api.replace('"', '\'')
    if ntype in self.typeLinks:
      G = G + ("%s%s%s%s: %s\n" % (self.tab, idn1, self.typeSeqLinks[ntype], idn2, linktext))
    else:
      G = G + ("%s%s%s%s: %s\n" % (self.tab, idn1, self.typeSeqLinksDefault, idn2, linktext))
    
    self.gLinks[group] = G

  def activate(self, group, service):

    idn1 = hashlib.md5(service.encode('utf-8')).hexdigest()

    if not group in self.gLinks:
      self.gLinks[group] = ''
    G = self.gLinks[group]
    
    if not idn1 in self.gNodes:
      self.gNodes[idn1] = '%sparticipant %s as %s\n' % (self.tab, idn1, service)

    G = G + '%sactivate %s\n' % (self.tab, idn1)
    
    self.gLinks[group] = G

  def deactivate(self, group, service):

    idn1 = hashlib.md5(service.encode('utf-8')).hexdigest()

    if not group in self.gLinks:
      self.gLinks[group] = ''
    G = self.gLinks[group]
    
    if not idn1 in self.gNodes:
      self.gNodes[idn1] = '%sparticipant %s as %s\n' % (self.tab, idn1, service)

    G = G + '%sdeactivate %s\n' % (self.tab, idn1)
    
    self.gLinks[group] = G

  def parallelStart(self, group, text):
    self.blockStart('%spar %s\n', group, text)

  def parallelAnd(self, group, text):
    self.blockStart('%sand %s\n', group, text)

  def parallelFinish(self, group, text):
    self.blockFinish(group, text)

  def altIf(self, group, text):
    self.blockStart('%salt %s\n', group, text)

  def altElse(self, group, text):
    self.blockStart('%selse %s\n', group, text)

  def altEnd(self, group, text):
    self.blockFinish(group, text)

  def optIf(self, group, text):
    self.blockStart('%sopt %s\n', group, text)

  def optEnd(self, group, text):
    self.blockFinish(group, text)
    
  def blockStart(self, block, group, text):

    if not group in self.gLinks:
      self.gLinks[group] = ''
    G = self.gLinks[group]
    
    G = G + (block % (self.tab, text))
    
    self.gLinks[group] = G

  def blockFinish(self, group, text):

    if not group in self.gLinks:
      self.gLinks[group] = ''
    G = self.gLinks[group]
    
    G = G + '%send\n' % (self.tab)
    
    self.gLinks[group] = G

  def drawFlow(self):
    G = "flowchart LR\n"
    for i in self.gNodes:
      if i in self.gGroups:
        G = G + self.gGroups[i]
      G = G + self.gNodes[i]
      if i in self.gGroups:
        G = G + self.tab + 'end\n'
    return G
  
  def drawSequence(self):
    G = "sequenceDiagram\n%sautonumber\n" % self.tab
    for i, v in self.gNodes.items():
      G = G + v
    for i, v in self.gLinks.items():
      G = G + v
    return G
  
  def finish(self):
    if self.typeDia == 'flowLR':
      return self.drawFlow()

    if self.typeDia == 'sequence':
      return self.drawSequence()

    return ''

