#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic

from diagrams import Cluster

class Domains(Basic):
  def __init__ (self):
    super(Domains, self).__init__()
    self.name = 'domains'
    self.fields = ['id', 'name', 'status', 'layer', 'link', 'comment']

  def graph(self, D, domain):
    id = domain.get('id', 'xz')
    sname = domain.get('name', 'xz').replace('"', '\'')
    status = domain.get('status', 'undef')
    link = domain.get('link', '')
    D.group(id, sname, status, link)
