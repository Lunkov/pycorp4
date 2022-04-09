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
    self.__verbose = verbose
    self.__name = ''
    self.__tab = '    '
    self.__typeDia = ''
    self.__gNodes = {}
    self.__gGroups = {}
    self.__gLinks = {}

  def new(self, typeDia, name):
    self.__name = name
    self.__typeDia = typeDia
    self.__gGroups = {}
    self.__gNodes = {}
    self.__gLinks = {}

  def node(self, id, name, group = '-', ntype = '', status = '', link = '', description = ''):
    self.__gNodes[id] = {'name': name, 'group': group, 'type': ntype, 'status': status}

  def group(self, id, name, status = '', link = ''):
    self.__gGroups[id] = {'name': name, 'status': status}

  def link(self, node_from, node_to, group = '-', tags = '', status = '', text = ''):
    idn1 = hashlib.md5(str(node_from).encode('utf-8') + str(node_to).encode('utf-8')).hexdigest()
    self.__gLinks[idn1] = {'node_from': node_from, 'node_to': node_to, 'text': text, 'status': status}

  def finish(self, filename):
    if self.__verbose > 0:
      print('LOG: Make diagram: %s' % filename)
    nn = {}
    try:
      with Diagram(self.name, show = False, filename = filename, outformat = 'png') as diag:
        for i, g in self.__gGroups.items():
          gname = g.get('name', 'undef')
          with Cluster(gname):
            for j, n in self.__gNodes.items():
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
        for k, lnk in self.__gLinks.items():
          if lnk['node_from'] in nn and lnk['item_to'] in nn:
            # print("LOG: Edge '%s' => '%s' : %s" % (nn[lnk['service_from']], nn[lnk['service_to']], lnk['text']), flush=True)
            if lnk['status'] == 'ok':
              nn[lnk['node_from']] >> Edge(label=lnk['text'], style="bold") >> nn[lnk['item_to']]
            else:
              nn[lnk['node_from']] >> Edge(label=lnk['text']) >> nn[lnk['item_to']]
    except Exception as e:
      print("ERR: Diagram: %s: %s" % (filename, str(e)))
      return False
