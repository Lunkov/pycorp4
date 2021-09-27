#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic
from .elog import ELog

class Links(Basic):
  def __init__ (self):
    super(Links, self).__init__()
    self.name = 'links'
    self.fields = ['id', 'api', 'src.data', 'status']

  def graphVIZ(self, G):
    for i, v in self.m.items():
      try:
        G.add_edge(v['api'], v['src.data'], weight = 0.2)
      except Exception as e:
        print("ERR: Link: %s => %s: %s" % (v['api'], v['src.data'], str(e)))
        elog = ELog()
        elog.log("HTTP_ERROR", "ERR: Link: %s => %s: %s" % (v['api'], v['src.data'], str(e)), '', '')


  def graph(self):
    G = ''
    tab = '    '
    id = service.get('id', 'xz')
    sname = service.get('name', 'xz')
    stype = service.get('type', 'service')
    status = service.get('status', 'undef')
    link = service.get('link', '')
    idn = hashlib.md5(id.encode('utf-8')).hexdigest()
    if stype == 'service':
      G = G + ("%s%s[\"%s\"]\n" % (tab, idn, sname))
    if stype == 'kafka':
      G = G + ("%s%s(\"%s\")\n" % (tab, idn, sname))
    if stype == 'db':
      G = G + ("%s%s[(\"%s\")]\n" % (tab, idn, sname))
    if status == 'undef':
      G = G + ("%sstyle %s fill:#111111,stroke:#333,stroke-width:4px\n" % (tab, idn))
    if status == 'deprecated':
      G = G + ("%sstyle %s fill:#aaaaaa,stroke:#333,stroke-width:2px\n" % (tab, idn))
    if status == 'ok':
      G = G + ("%sstyle %s fill:#00ee00,stroke-width:2px\n" % (tab, idn))
    if link != "":
      G = G + ("%sclick %s \"%s\" _blank\n" % (tab, idn, link))
    return G
