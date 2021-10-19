#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import logging
import os

import hashlib

from diagrams import Cluster, Diagram, Edge


from diagrams.gcp.compute import Functions
from diagrams.aws.integration import SQS
from diagrams.aws.network import ELB
from diagrams.aws.database import RDS

class Dia():
  def __init__ (self, verbose):
    self.verbose = verbose
    self.tab = '    '
    self.typeDia = ''
    self.gNodes = {}
    self.gGroups = {}
    self.gLinks = {}
    
  def new(self, typeDia, name):
    self.name = name
    self.typeDia = typeDia
    self.gGroups = {}
    self.gNodes = {}
    self.gLinks = {}

  def node(self, id, name, group = '-', ntype = '', status = '', link = '', description = ''):
    self.gNodes[id] = {'name': name, 'group': group, 'type': ntype, 'status': status}

  def group(self, id, name, status = '', link = ''):
    self.gGroups[id] = {'name': name, 'status': status}

  def link(self, service_from, service_to, group = '-', tags = '', status = '', text = ''):
    idn1 = hashlib.md5(service_from.encode('utf-8') + service_to.encode('utf-8')).hexdigest()
    self.gLinks[idn1] = {'service_from': service_from, 'service_to': service_to, 'text': text, 'status': status}

  def finish(self, filename):
    if self.verbose > 0:
      print('LOG: Make diagram: %s' % filename)
    nn = {}
    try:
      with Diagram(self.name, show = False, filename = filename, outformat = 'png') as diag:
        for i, g in self.gGroups.items():
          gname = g.get('name', 'undef')
          with Cluster(gname):
            for j, n in self.gNodes.items():
              if n.get('group', 'undef') == i:
                name = n.get('name', 'undef')
                ntype = n.get('type', 'service')
                if ntype == 'service':
                  nn[j] = Functions(j)
                if ntype == 'kafka':
                  nn[j] = SQS(j)
                if ntype == 'bff':
                  nn[j] = ELB(j)
                if ntype == 'db':
                  nn[j] = RDS(j)
        for k, lnk in self.gLinks.items():
          if lnk['service_from'] in nn and lnk['service_to'] in nn:
            # print("LOG: Edge '%s' => '%s' : %s" % (nn[lnk['service_from']], nn[lnk['service_to']], lnk['text']), flush=True)
            if lnk['status'] == 'ok':
              nn[lnk['service_from']] >> Edge(label=lnk['text'], style="bold") >> nn[lnk['service_to']]
            else:
              nn[lnk['service_from']] >> Edge(label=lnk['text']) >> nn[lnk['service_to']]
    except Exception as e:
      print("ERR: Diagram: %s: %s" % (filename, str(e)))
      return False
