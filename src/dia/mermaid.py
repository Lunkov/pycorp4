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
  def __init__ (self, config: dict):
    self.__tab = '    '
    self.__name = ''
    self.__typeDia = ''

    self.__gNodes = {}
    self.__gClasses = {}
    self.__gFields = {}
    self.__gGroups = {}
    self.__gLinks = {}

    self.__typeNodesDef = '["%s"]'
    self.__typeNodes = {}
    if 'objects' in config:
      self.__typeNodes = config['objects']
    self.__statusNodes = {}
    if 'objects-status' in config:
      self.__statusNodes = config['objects-status']

    self.__typeLinksDefault = '-...-|%s|'
    self.__typeLinks = {}
    if 'links' in config:
      self.__typeLinks = config['links']
    self.__statusLinks = {}
    if 'links-status' in config:
      self.__statusLinks = config['links-status']

    self.__typeSeqLinksDefault = '->>'
    self.__typeSeqLinks = {}
    if 'links' in config:
      self.__typeSeqLinks = config['links']

  def new(self, typeDia, name):
    self.__name = name
    self.__typeDia = typeDia
    self.__gGroups = {}
    self.__gNodes = {}
    self.__gClasses = {}
    self.__gFields = {}
    self.__gLinks = {}

  def makeLegend(self, name):
    self.new('flowLR', name)

    self.group('status', 'Status of nodes')
    for i, v in self.__statusNodes.items():
      if i == 'undef':
        self.node(i, i, 'status', 'service', '-', '', i)
      else:
        self.node(i, i, 'status', 'service', i, '', i)

    ki = 0
    kc = int(len(self.__typeNodes) / 5)
    self.group('type%d' % kc, 'Types of nodes %d' % kc)
    for i, v in self.__typeNodes.items():
      ki = ki + 1
      self.node(i, i, ('type%d' % kc), i, 'ok', '', i)
      if ki % 5 == 0:
        kc = kc - 1
        self.group('type%d' % kc, 'Types of nodes %d' % kc)

    self.group('typelinks', 'Types of links')
    for i, v in self.__typeLinks.items():
      idn1 = hashlib.md5((i+'-srv1').encode('utf-8')).hexdigest()
      idn2 = hashlib.md5((i+'-srv2').encode('utf-8')).hexdigest()
      self.node(idn1, 'Service 1', 'typelinks', 'service', 'ok', '', i)
      self.node(idn2, 'Service 2', 'typelinks', 'service', 'ok', '', i)
      self.link(idn1, idn2, 'typelinks', '', i, i)

    return self.finish()

  def __node(self, id, name, ntype = '', description = ''):
    idn = self.__genUID(id)
    nname = name.replace('"', '\'').replace('(', ' ').replace(')', ' ') #.replace(':', '\:').replace('.', '\.')
    ndescription = description.replace('"', "\'").replace(':', '\\:').replace('.', '\\.')
    N = ''
    if ntype in self.__typeNodes:
      N = self.__typeNodes[ntype].get('view', '[%s]') % (nname)
    else:
      N = self.__typeNodesDef % (nname)
    return idn, ("%s%s%s\n" % (self.__tab, idn, N))    

  def __genUID(self, s):
    if type(s) is str:
      return hashlib.md5(s.encode('utf-8')).hexdigest()
    ret = ''
    for i in s:
      ret = ret + '.' + i
    return hashlib.md5(ret.encode('utf-8')).hexdigest()

  def node(self, id, name, group = '-', ntype = '', status = '', link = '', description = ''):
    if not group in self.__gNodes:
      self.__gNodes[group] = ''
    G = self.__gNodes[group]
    idn, N = self.__node(id, name, ntype, description)

    G = G + N

    if status in self.__statusNodes:
      G = G + ("%sstyle %s %s;\n" % (self.tab, idn, self.__statusNodes[status]))
    #else:
    #  G = G + ("%sstyle %s %s;\n" % (self.tab, idn, self.statusNodes['undef']))

    if link != '':
      # COMMENT: For HTTP ref => G = G + ("%sclick %s \"%s\" _blank\n" % (self.tab, idn, link))
      G = G + ("%sclick %s call nodeClick(\"%s\")\n" % (self.__tab, idn, id))
    self.__gNodes[group] = G

  def data(self, id, name, group = '-', ntype = '', sizeof = 0):
    if not group in self.__gClasses:
      self.__gClasses[group] = {}
    if not id in self.__gClasses[group]:
      self.__gClasses[group][id] = ''
    G = self.__gClasses[group][id]
    G = G + ("%sclass %s{\n" % (self.__tab, name))
    if sizeof > 0:
      G = G + ("%ssizeof(%d)\n" % (self.__tab, sizeof))
    self.__gClasses[group][id] = G

  def dataFields(self, dataid, name, ntype = 'undef'):
    if not dataid in self.__gFields:
      self.__gFields[dataid] = ''
    self.__gFields[dataid] = ("%s%s%s : %s\n" % (self.__gFields[dataid], self.__tab, name, ntype))

  def dataLink(self, data_from, data_to, ltype = '', text = ''):
    idn = self.__genUID([data_from, data_to, ltype])
    if not idn in self.__gLinks:
      self.__gLinks[idn] = ''

    G = self.__gLinks[idn]

    G = G + ("%s%s \"\" --> \"\" %s : %s\n" % (self.__tab, data_from, data_to, text))

    self.__gLinks[idn] = G

  def group(self, id, name, status = '', link = ''):
    if not id in self.__gGroups:
      self.__gGroups[id] = ''
    G = self.__gGroups[id]

    idn = self.__genUID('group:'+id)
    G = G + ("%ssubgraph %s[\"%s\"]\n" % (self.__tab, idn, name.replace('"', '\'')))

    # TODO
    #if link != "":
    #  G = G + ("%sclick %s \"%s\" _blank\n" % (self.tab, idn, link))

    self.__gGroups[id] = G

  def link(self, node_from, node_to, group = '-', tags = '', ltype = '', text = ''):
    if not group in self.__gNodes:
      self.__gNodes[group] = ''

    G = self.__gNodes[group]

    idn1 = self.__genUID(node_from)
    idn2 = self.__genUID(node_to)
    linktext = ''
    if len(text) > 0:
      linktext = text.replace('"', '\'')

    N = ''
    if ltype in self.__typeLinks:
      N = self.__typeLinks[ltype].get('view', '-- %s --') % linktext
    else:
      print('WRN: Link type not found "%s"' % ltype)
      N = self.__typeLinksDefault % linktext
    N = N.replace('||', '')
    G = G + ("%s%s %s %s\n" % (self.__tab, idn1, N, idn2))
    #if status in self.statusLinks:
    #  G = G + ("%sstyle %s %s;\n" % (self.tab, idn1, self.statusLinks[status]))

    self.__gNodes[group] = G

  def sequenceNote(self, group, node, text = ''):
    if text == '':
      return
    if not group in self.__gLinks:
      self.__gLinks[group] = ''

    idn = self.__genUID(node)
    G = self.__gLinks[group]
    G = G + ("%sNote right of %s: %s\n" % (self.__tab, idn, text))
    self.__gLinks[group] = G

  def sequence(self, group, node_from, node_to, api = '', ntype = ''):

    idn1 = self.__genUID(node_from)
    idn2 = self.__genUID(node_to)

    if not idn1 in self.gNodes:
      self.gNodes[idn1] = '%sparticipant %s as %s\n' % (self.__tab, idn1, node_from)
    if not idn2 in self.gNodes:
      self.gNodes[idn2] = '%sparticipant %s as %s\n' % (self.__tab, idn2, node_to)

    if not group in self.gLinks:
      self.gLinks[group] = ''

    G = self.gLinks[group]

    linktext = ''
    if api and len(api) > 0:
      linktext = api.replace('"', '\'')
    if ntype in self.typeLinks:
      G = G + ("%s%s%s%s: %s\n" % (self.__tab, idn1, self.typeSeqLinks[ntype], idn2, linktext))
    else:
      G = G + ("%s%s%s%s: %s\n" % (self.__tab, idn1, self.typeSeqLinksDefault, idn2, linktext))

    self.gLinks[group] = G

  def activate(self, group, node):

    idn1 = self.__genUID(node)

    if not group in self.gLinks:
      self.gLinks[group] = ''
    G = self.gLinks[group]
    
    if not idn1 in self.gNodes:
      self.gNodes[idn1] = '%sparticipant %s as %s\n' % (self.__tab, idn1, node)

    G = G + '%sactivate %s\n' % (self.tab, idn1)
    
    self.gLinks[group] = G

  def deactivate(self, group, node):

    idn1 = self.__genUID(node)

    if not group in self.__gLinks:
      self.__gLinks[group] = ''
    G = self.__gLinks[group]
    
    if not idn1 in self.gNodes:
      self.gNodes[idn1] = '%sparticipant %s as %s\n' % (self.__tab, idn1, node)

    G = G + '%sdeactivate %s\n' % (self.__tab, idn1)
    
    self.__gLinks[group] = G

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

    if not group in self.__gLinks:
      self.__gLinks[group] = ''
    G = self.__gLinks[group]

    G = G + (block % (self.tab, text))

    self.__gLinks[group] = G

  def blockFinish(self, group, text):

    if not group in self.__gLinks:
      self.__gLinks[group] = ''
    G = self.__gLinks[group]

    G = G + '%send\n' % (self.tab)

    self.__gLinks[group] = G

  def drawFlow(self):
    G = "flowchart LR\n"
    for i in self.__gNodes:
      if i in self.__gGroups:
        G = G + self.__gGroups[i]
      G = G + self.__gNodes[i]
      if i in self.__gGroups:
        G = G + self.__tab + 'end\n'
    return G

  def drawData(self):
    G = 'classDiagram\n  direction RL\n'
    for g in self.__gClasses:
      if g in self.__gGroups:
        G = G + self.__gGroups[g]
      for i in self.__gClasses[g]:
        G = G + self.__gClasses[g][i]
        if i in self.__gFields:
          G = G + self.__gFields[i]
        G = G + self.__tab + '}\n'
      if g in self.__gGroups:
        G = G + self.__tab + 'end\n'
    for i in self.__gLinks:
      G = G + self.__gLinks[i]
    return G

  def drawSequence(self):
    G = "sequenceDiagram\n%sautonumber\n" % self.tab
    for i, v in self.__gNodes.items():
      G = G + v
    for i, v in self.__gLinks.items():
      G = G + v
    return G

  def finish(self):
    if self.__typeDia == 'flowLR':
      return self.drawFlow()

    if self.__typeDia == 'data':
      return self.drawData()

    if self.__typeDia == 'sequence':
      return self.drawSequence()

    return ''

