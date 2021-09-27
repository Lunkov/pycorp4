#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic

from diagrams import Cluster

class Domains(Basic):
  def __init__ (self):
    super(Domains, self).__init__()
    self.name = 'domains'
    self.fields = ['id', 'name', 'status', 'layer', 'link', 'comment']

  def graphWULF(self, G, labels):
    for i, v in self.m.items():
      G.add_node(i)
      labels[i] = i
    for n, data in G.nodes(data=True):
      if n in self.m:
        data['size'] = 1
        data['c'] = '#FF5f02'

  def graphVIZ(self, G):
    for i, v in self.m.items():
      c = '#11FF11'
      if v['status'] != 'ok':
        c = '#777777'
      G.add_node(i, label = i, color = c, size = 30, group = v['name'])

  def htmlAll(self):
    p = "<h1>Домены</h1>"
    p = p + "<table class='table'>"
    p = p + "<tr><td>Код</td><td>Наименование</td><td>Статус</td><td>Ссылка</td></tr>"
    for k, v in self.m.items():
      p = p + "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (k, v.get('name', ''), v.get('status', ''), v.get('link', ''))
    p = p + "</table>"
    return p

  def graphDia(self, D, name):
    domain = self.get(name)
    if (not name in self.dia) or (self.dia[name] == None):
      self.dia[name] = Cluster(domain.get('name', ''))
    return self.dia[name]

  def graph(self, D, domain):
    id = domain.get('id', 'xz')
    sname = domain.get('name', 'xz').replace('"', '\'')
    status = domain.get('status', 'undef')
    link = domain.get('link', '')
    D.group(id, sname, status, link)
