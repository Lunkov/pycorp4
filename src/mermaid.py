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
from .servicelinks import ServiceLinks

import hashlib

import graphviz
import networkx as nx
from netwulf import visualize
from pyvis.network import Network
from diagrams import Diagram


from diagrams.gcp.compute import Functions
from diagrams.aws.integration import SQS
from diagrams.aws.network import ELB
from diagrams.aws.database import RDS

class Mermaid():
  def __init__ (self):
    self.tab = '    '
    self.typeDia = ''
    self.dia = {}
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

    self.typeLinksDefault = 'o--o'
    self.typeLinks = {
     'deprecated':   'x-.-x',
     'plan':         '-.-',
     'dev':          '-.->',
     'ok':           'o-->',
    }
    self.statusNodes = {
     'undef':        "fill:#111111,stroke:#333,stroke-width:4px",
     'deprecated':   "fill:#aaaaaa,stroke:#333,stroke-width:2px",
     'ok':           "fill:#00ee00,stroke-width:2px"
    }
    self.header = """
          <head>

              <meta charset="utf-8">
              <meta http-equiv="X-UA-Compatible" content="IE=edge">
              <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
              <meta name="description" content="">
              <meta name="author" content="">

              <title>Schema</title>

              <!-- Custom fonts for this template-->
              <link href="/vendor/fontawesome-free/css/all.min.css" rel="stylesheet" type="text/css">
              <link
                  href="https://fonts.googleapis.com/css?family=Nunito:200,200i,300,300i,400,400i,600,600i,700,700i,800,800i,900,900i"
                  rel="stylesheet">

              <!-- Custom styles for this template-->
              <link href="/css/sb-admin-2.min.css" rel="stylesheet">

          </head>
          <body id="page-top">
           <script src="/vendor/jquery/jquery.min.js"></script>
           <script src="/vendor/bootstrap/js/bootstrap.bundle.min.js"></script>
           <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
           
           <script>
          var services = {};
          $.getJSON("/data/services.json", function( json ) {
            services = new Map(Object.entries(json));
           });
           
            var config = {
            startOnLoad:true,
            htmlLabels:true,
            securityLevel: 'loose',
            flowchart:{
                    useMaxWidth:false,
                }
           };
           mermaid.initialize(config);
           mermaid.parseError = function(err,hash){  console.log(err);};
           
           var nodeClick = function(id_service) {
           console.log("**", services);
           console.log("**", id_service);
           console.log("**", services.get(id_service));
              if(services.get(id_service)) {
                $("#block-name").html(services.get(id_service).name);
                $("#block-description").html("Описание: " + services.get(id_service).description);
                $("#block-dialink").html("<a href=\\"/dia/service/"+id_service+".html\\" target=_blank>Схема сервиса</a>");
                $("#block-link").html("<a href=\\"/service/"+id_service+".html\\" target=_blank>"+services.get(id_service).name+"</a>");
                $("#block-linkwiki").html("<a href=\\""+services.get(id_service).link+"\\" target=_blank>Wiki</a>");
                $("#block-swagger").html("<a href=\\""+services.get(id_service).swagger+"\\" target=_blank>Swagger</a>");
              }
              $("#block-dlg").modal();
           }
           </script>
            <div class="modal" tabindex="-1" role="dialog" id="block-dlg">
              <div class="modal-dialog" role="document">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title" id="block-name"></h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                      <span aria-hidden="true">&times;</span>
                    </button>
                  </div>
                  <div class="modal-body">
                    <p id="block-description"></p>
                    <p id="block-link"></p>
                    <p id="block-linkwiki"></p>
                    <p id="block-swagger"></p>
                  </div>
                  <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                  </div>
                </div>
              </div>
            </div>             
        """

  def new(self, typeDia, name):
    self.name = name
    self.typeDia = typeDia
    self.dia = {}
    self.gGroups = {}
    self.gNodes = {}
    self.gLinks = {}

  def node(self, id, name, group = '-', ntype = '', status = '', link = '', description = ''):
    if self.typeDia == 'dia':
      if (not name in self.dia) or (self.dia[name] == None):
        if ntype == 'service':
          self.dia[name] = Functions(name)
        if ntype == 'kafka':
          self.dia[name] = SQS(name)
        if ntype == 'bff':
          self.dia[name] = ELB(name)
        if ntype == 'db':
          self.dia[name] = RDS(name)
      return
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
      G = G + ("%s%s %s%s %s\n" % (self.tab, idn1, self.typeLinksDefault, linktext, idn2))
    
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

    if not group in self.gLinks:
      self.gLinks[group] = ''
    G = self.gLinks[group]
    
    G = G + '%spar %s\n' % (self.tab, text)
    
    self.gLinks[group] = G

  def parallelAnd(self, group, text):

    if not group in self.gLinks:
      self.gLinks[group] = ''
    G = self.gLinks[group]
    
    G = G + '%sand %s\n' % (self.tab, text)
    
    self.gLinks[group] = G

  def parallelFinish(self, group, text):

    if not group in self.gLinks:
      self.gLinks[group] = ''
    G = self.gLinks[group]
    
    G = G + '%send\n' % (self.tab)
    
    self.gLinks[group] = G

  def drawFlow(self, G):
    G = G + "\nflowchart LR\n"
    for i in self.gNodes:
      if i in self.gGroups:
        G = G + self.gGroups[i]
      G = G + self.gNodes[i]
      if i in self.gGroups:
        G = G + self.tab + 'end\n'
    return G
  
  def drawSequence(self, G):
    G = G + "\nsequenceDiagram\n%sautonumber\n" % self.tab
    for i, v in self.gNodes.items():
      G = G + v
    for i, v in self.gLinks.items():
      G = G + v
    return G
    
  def finish(self):
    G = self.header
    G = G + ("<div class=\"mermaid\" id=\"%s\">" % self.name)
    if self.typeDia == 'flowLR':
      G = self.drawFlow(G)

    if self.typeDia == 'sequence':
      G = self.drawSequence(G)

    G = G + '</div>\n</body>\n'

    return G

  def save(self, filename):
    text_file = codecs.open(filename, 'w', 'utf-8')
    text_file.write(self.G)
    text_file.close()
