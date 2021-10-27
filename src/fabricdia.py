#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import logging
import os

from .mermaid import Mermaid
from .mermaidCLI import MermaidCLI
from .dia import Dia


class FabricDia():
  def __init__ (self, fs, html, verbose):
    self.verbose = verbose
    self.fs = fs
    self.html = html
    self.mermaidcli = MermaidCLI(verbose)

  def drawBlockDiagramLegend(self, name, filename):
    D = Mermaid()
    dia = D.getLegend(name)
    if not self.fs.writeFile(filename + '.mmd', dia):
      return

    self.mermaidcli.makePNG(self.fs.getPathHTML(), filename + '.mmd')
    self.html.render('components/diagram_template.html', filename + '.html', {'dia_id': name, 'dia_scheme': dia})

    
  def drawBlockDiagram(self, name, domains, services, srvlinks, filename):
    D = Mermaid()
    D.new('flowLR', name)
    
    for j, domain in domains.items():
      D.group(domain.get('id', 'xz'),
              domain.get('name', 'xz').replace('"', '\''),
              domain.get('status', 'undef'),
              domain.get('link', ''))
      
    for i, service in services.items():
      D.node(service.get('id', 'xz'),
             service.get('name', 'xz'),
             service.get('domain', 'undef'), 
             service.get('type', 'service'),
             service.get('status', 'undef'),
             service.get('link', ''),
             service.get('description', ''))

    for i, link in srvlinks.items():
      D.link(link.get('service_from', 'xz'),
             link.get('service_to', 'xz'),
             link.get('domain', ''),
             link.get('tags', ''),
             link.get('status', ''),
             link.get('description', ''))

    dia = D.finish()
    if not self.fs.writeFile(filename + '.mmd', dia):
      return

    self.mermaidcli.makePNG(self.fs.getPathHTML(), filename + '.mmd')
    self.html.render('components/diagram_template.html', filename + '.html', {'dia_id': name, 'dia_scheme': dia})

    D = Dia(self.verbose)
    D.new('dia', name)
    
    for j, domain in domains.items():
      D.group(domain.get('id', 'xz'),
              domain.get('name', 'xz').replace('"', '\''),
              domain.get('status', 'undef'),
              domain.get('link', ''))
      
    for i, service in services.items():
      D.node(service.get('id', 'xz'),
             service.get('name', 'xz'),
             service.get('domain', 'undef'), 
             service.get('type', 'service'),
             service.get('status', 'undef'),
             service.get('link', ''),
             service.get('description', ''))

    for i, link in srvlinks.items():
      D.link(link.get('service_from', 'xz'),
             link.get('service_to', 'xz'),
             link.get('domain', ''),
             link.get('tags', ''),
             link.get('status', ''),
             link.get('description', ''))

    D.finish(filename+'.dia')

  def drawSequenceDiagram(self, name, seq, services, filename):
    D = Mermaid()
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
        if 'activate' in v:
          D.activate('main', v['activate'])
        if 'deactivate' in v:
          D.deactivate('main', v['deactivate'])
        if 'parallel-finish' in v:
          D.parallelFinish('main', v['parallel-finish'])
    
    dia = D.finish()
    if not self.fs.writeFile(filename + '.mmd', dia):
      return
    self.mermaidcli.makePNG(self.fs.getPathHTML(), filename + '.mmd')
    self.html.render('components/diagram_template.html', filename + '.html', {'dia_id': name, 'dia_scheme': dia})
