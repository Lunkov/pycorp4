#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jinja2
import hashlib
import pdfkit
from src.helpers.fs import FS

class HTML():
  def __init__ (self, fs: FS, verbose = False):
    self.__verbose = verbose
    self.__fs = fs
    self.__templates = {}
    self.__templateLoader = jinja2.FileSystemLoader(searchpath = self.fs.getPathTemplates())
    self.__templateEnv = jinja2.Environment(loader = self.templateLoader)

  def render(self, tmplfile, dstfile, prop = {}):
    if not tmplfile in self.templates:
      self.__templates[tmplfile] = self.__templateEnv.get_template(tmplfile)

    self.__fs.writeFile(dstfile, self.__templates[tmplfile].render(prop, md5=self.__fs.md5String))

  def html2pdf(self, html_path, pdf_path):
    """
    Convert html to pdf using pdfkit which is a wrapper of wkhtmltopdf
    """
    options = {
        'page-size': 'a4',
        'margin-top': '0.35in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None
    }
    with open(html_path) as f:
      pdfkit.from_file(f, pdf_path, options=options)
