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
  def __init__ (self):
    self.tab = '    '
    self.typeDia = ''
    self.gNodes = {}
    self.gGroups = {}
    self.gLinks = {}
    self.typeNodesDef = ['[', ']']
    self.typeNodes = {
     'default':   ['[', ']'],
     'undef':     ['[', ']'],
     'kafka':     ['(', ')'],
     'rabbitmq':  ['(', ')'],
     'service':   ['{{', '}}'],
     'app':       ['[[', ']]'],
     'db':        ['[(', ')]'],
     'storage':   ['[(', ')]'],
     'bff':       ['[/', '\]'],
    }
    self.typeSeqLinksDefault = '->>'
    self.typeSeqLinks = {
     'deprecated':   '-->>',
     'plan':         '-->>',
     'dev':          '-->>',
     'ok':           '-->',
    }

    self.typeLinksDefault = '-...-'
    self.typeLinks = {
     'deprecated':   '-...-',
     'plan':         '-..-',
     'dev':          '-.->',
     'ok':           'o-->',
    }
    self.statusLinks = {
     'undef':        "fill:#111111,stroke:#333,stroke-width:1px",
     'deprecated':   "fill:#aa0000,stroke:#333,stroke-width:2px",
     'ok':           "fill:#00ee00,stroke-width:2px"
    }
    self.statusNodes = {
     'undef':        "fill:#111111,stroke:#333,stroke-width:4px",
     'deprecated':   "fill:#aaaaaa,stroke:#333,stroke-width:2px",
     'ok':           "fill:#00ee00,stroke-width:2px"
    }

  def new(self, typeDia, name):
    self.name = name
    self.typeDia = typeDia
    self.gGroups = {}
    self.gNodes = {}
    self.gLinks = {}

  def node(self, id, name, group = '-', ntype = '', status = '', link = '', description = ''):
    if not group in self.gNodes:
      self.gNodes[group] = ''
    G = self.gNodes[group]
    idn = hashlib.md5(id.encode('utf-8')).hexdigest()
    nname = name.replace('"', '\'') #.replace(':', '\:').replace('.', '\.')
    ndescription = description.replace('"', '\'').replace(':', '\:').replace('.', '\.')
    if ntype in self.typeNodes:
      G = G + ("%s%s%s\"%s\"%s\n" % (self.tab, idn, self.typeNodes[ntype][0], nname, self.typeNodes[ntype][1]))
    else:
      G = G + ("%s%s%s\"%s\"%s\n" % (self.tab, idn, self.typeNodesDef[0], nname, self.typeNodesDef[1]))
    
    if status in self.statusNodes:
      G = G + ("%sstyle %s %s;\n" % (self.tab, idn, self.statusNodes[status]))

    if link != "":
      # G = G + ("%sclick %s \"%s\" _blank\n" % (self.tab, idn, link))
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
      linktext = "|%s|" % text.replace('"', '\'')
    if status in self.typeLinks:
      G = G + ("%s%s %s%s %s\n" % (self.tab, idn1, self.typeLinks[status], linktext, idn2))
    else:
      print('LOG: status not found "%s"' % status)
      G = G + ("%s%s %s%s %s\n" % (self.tab, idn1, self.typeLinksDefault, linktext, idn2))
    
    #if status in self.statusLinks:
    #  G = G + ("%sstyle %s %s;\n" % (self.tab, idn1, self.statusLinks[status]))

    self.gNodes[group] = G

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

