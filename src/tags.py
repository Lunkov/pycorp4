#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import Basic

class Tags(Basic):
  def __init__ (self):
    super(Tags, self).__init__()
    self.name = 'tags'
    self.fields = ['id', 'name']

  def htmlAll(self):
    p = "<h1>Тэги</h1>"
    p = p + "<table class='table'>"
    p = p + "<tr><td>Код</td><td>Наименование</td>"
    for k, v in self.m.items():
      p = p + "<tr><td>%s</td><td>%s</td></tr>" % (k, v.get('name', ''))
    p = p + "</table>"
    return p
