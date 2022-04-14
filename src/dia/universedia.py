#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import logging
import os
import math
from pprint import pprint

from .mermaid import Mermaid
from .mermaidCLI import MermaidCLI
from .dia import Dia

from src.cfg import Cfg
from src.helpers.fs import FS
from src.helpers.html import HTML


class UniverseDia():
  def __init__ (self, fs: FS, html: HTML, config: Cfg, verbose = 0):
    self.__verbose = verbose
    self.__config = config
    self.__fs = fs
    self.__html = html
    self.__mermaidcli = MermaidCLI(verbose)
    self.__template_diagram = os.path.realpath('html/components/diagram_template.html')
    self.__template_diagram_simple = os.path.realpath('html/components/diagram_template_simple.html')

  def drawBlockDiagramLegend(self, name: str, filename: str):
    cfg = {}
    if not self.__config is None:
      cfg = self.__config.getCfg('mermaid')
    D = Mermaid(cfg)
    dia = D.makeLegend(name)
    if not self.__fs.writeFile(filename + '.mmd', dia):
      return

    self.__mermaidcli.makePNG(self.__fs.getPathHTML(), filename + '.mmd')
    if os.path.isfile(self.__template_diagram_simple):
      self.__html.render(self.__template_diagram_simple, filename + '.html', {'dia_id': name, 'dia_scheme': dia})

  def __draw(self, D, groups: dict, nodes: dict, links: dict):
    if not groups is None:
      for j, group in groups.items():
        if group.get('id', '') != '':
          D.group(group.get('id', 'undef'),
                  group.get('name', group.get('id', 'undef')).replace('"', '\''),
                  group.get('parent', ''),
                  group.get('status', 'undef'),
                  group.get('link', ''))

    if not nodes is None:
      for i, node in nodes.items():
        if node.get('id', '') != '':
          D.node(node.get('id', 'undef'),
                 node.get('name', node.get('id', 'undef')),
                 node.get('parent', 'undef'), 
                 node.get('type', 'service'),
                 node.get('status', 'undef'),
                 node.get('link', ''),
                 node.get('description', ''))

    if not links is None:
      for i, link in links.items():
        if link.get('link_from', '') != '' and link.get('link_to', '') != '':
          D.link(link.get('link_from', 'xz'),
                 link.get('link_to', 'xz'),
                 link.get('parent', 'undef'),
                 link.get('tags', ''),
                 link.get('type', 'data'),
                 link.get('description', ''))

  def drawBlockDiagram(self, name: str, groups: dict, nodes: dict, links: dict, filename: str):
    cfg = {}
    if not self.__config is None:
      cfg = self.__config.getCfg('mermaid')
    D = Mermaid(cfg)
    D.new('flowLR', name)

    self.__draw(D, groups, nodes, links)

    dia = D.finish()
    if not self.__fs.writeFile(filename + '.mmd', dia):
      return

    self.__renderMermaid(filename, name, dia, '', groups, nodes)

    D = Dia(self.__verbose)
    D.new('dia', name)

    self.__draw(D, groups, nodes, links)

    D.finish(filename+'.dia')

  def drawClassDiagram(self, name: str, nodes: dict, functions: dict, dataSets: dict, dataFields: dict, links: dict, filename: str):
    cfg = {}
    if not self.__config is None:
      cfg = self.__config.getCfg('mermaid')
    D = Mermaid(cfg)
    D.new('data', name)

    for i, dataSet in nodes.items():
      classname = i.replace('-', '_').replace('.', '_')
      classtype = dataSet.get('type', '')
      D.classInit(classname,
                  dataSet.get('name', '').replace('-', '_').replace('.', '_'),
                  'area 1', classtype, dataSet.get('sizeof', 0))
      if 'functions' in dataSet:
        for fname in dataSet['functions']:
          codename = "%s.%s"
          pprint(functions[fname])
          if fname in functions:
            D.classFunction(classname, fname, functions[fname].get('input', ''),
                                           functions[fname].get('output', ''),
                                           functions[fname].get('use', ''))
          else:
            D.classFunction(classname, fname)
      if (classtype == 'queue' or classtype == 'table') and ('data' in dataSet):
        if dataSet['data'] in dataSets:
          if 'children' in dataSets[dataSet['data']]:
            for ch in dataSets[dataSet['data']]['children']:
              fch = dataSet['data'] + '.' + ch
              if fch in dataFields:
                D.classFields(classname, ch, dataFields[fch].get('type', ''))
                continue
              if ch in dataFields:
                D.dataFields(classname, ch, dataFields[ch].get('type', ''))


    #for i, dataField in self.w.getDataFields().get().items():
    #  D.dataFields(dataField.get('data', 'undef'), i, dataField.get('type', ''))

    for i, link in links.items():
      if link.get('type', '') == 'data':
        link_to = link.get('link_from', 'xz').replace('-', '_').replace('.', '_')
        link_from = link.get('link_to', 'xz').replace('-', '_').replace('.', '_')
        if link_to != '' and link_from != '':
          D.classLink(link_to,
                    link_from,
                    link.get('type', ''),
                    link.get('description', ''))

    dia = D.finish()
    
    self.__renderMermaid(filename, name, dia, '', {}, nodes)


  def drawSequenceDiagram(self, name, seq, nodes, filename):
    cfg = {}
    if not self.__config is None:
      cfg = self.__config.getCfg('mermaid')
    D = Mermaid(cfg)
    D.new('sequence', seq.get('name', ''))

    if hasattr(seq['sequence'], "__len__"):
      for v in seq['sequence']:
        if 'parallel-start' in v:
          D.parallelStart('main', v['parallel-start'])
        if 'alt-if' in v:
          D.altIf('main', v['alt-if'])
        if 'alt-else' in v:
          D.altElse('main', v['alt-else'])
        if 'alt-end' in v:
          D.altEnd('main', v['alt-end'])
        if 'opt-if' in v:
          D.optIf('main', v['opt-if'])
        if 'opt-end' in v:
          D.optIf('main', v['opt-end'])
        if 'parallel-and' in v:
          D.parallelAnd('main', v['parallel-and'])
        if 'from' in v:
          D.sequence('main', v.get('from', 'undef'), v.get('to', 'undef'), v.get('api', v.get('answer', '')), v.get('type', 'ok'))
        if 'from' in v and (v.get('type', 'undef') == 'answer'):
          if v['from'] in nodes:
            if 'rt_99' in nodes[v['from']]:
              if nodes[v['from']]['rt_99'] != '' and nodes[v['from']]['max_rps'] != '':
                D.sequenceNote('main', v['from'], '99%% responce time %s ms, max %s rps' % (nodes[v['from']]['rt_99'], nodes[v['from']]['max_rps']))
              else:
                if services[v['from']]['rt_99'] != '':
                  D.sequenceNote('main', v['from'], '99%% responce time %s ms, max %s rps' % (nodes[v['from']]['rt_99'], nodes[v['from']]['max_rps']))
        if 'activate' in v:
          D.activate('main', v['activate'])
        if 'deactivate' in v:
          D.deactivate('main', v['deactivate'])
        if 'parallel-finish' in v:
          D.parallelFinish('main', v['parallel-finish'])

    dia = D.finish()
    
    self.__renderMermaid(filename, name, dia, iw, groups, nodes)


  def __renderMermaid(self, filename, name, dia, iw, groups, nodes):
    if not self.__fs.writeFile(filename + '.mmd', dia):
      return

    sz = 500
    if groups is None:
      if not nodes is None:
        sz = 50 * len(nodes)
    else:
      sz = 500 * len(groups)
    self.__mermaidcli.makePNG(self.__fs.getPathHTML(), filename + '.mmd', sz)
    if os.path.isfile(self.__template_diagram_simple):
      self.__html.render(self.__template_diagram, filename + '.html', {'wsname': iw, 'dia_id': name, 'dia_scheme': dia})
