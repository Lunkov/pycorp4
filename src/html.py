#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jinja2

class HTML():
  def __init__ (self, fs, verbose):
    self.verbose = verbose
    self.fs = fs
    self.templates = {}
    self.templateLoader = jinja2.FileSystemLoader(searchpath = self.fs.getPathTemplates())
    self.templateEnv = jinja2.Environment(loader = self.templateLoader)

  def render(self, tmplfile, dstfile, prop = {}):
    if not tmplfile in self.templates:
      self.templates[tmplfile] = self.templateEnv.get_template(tmplfile)

    self.fs.writeFile(dstfile, self.templates[tmplfile].render(prop))

  def getTemplatePath():
    return self.templatesPath
