#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from .fs import FS

class Installer():
  def __init__ (self, fs: FS, verbose = 0):
    self.__fs = fs
    self.__verbose = verbose

  def update(self):
    # prepare Static Directory
    self.__fs.mkDir(self.__fs.getPathHTML() + '/%s',
                   ['static'])
    
    self.__fs.rsync(self.__fs.getPathTemplates() + '/static/%s', self.__fs.getPathHTML() + '/static/%s', ['js', 'css', 'scss', 'vendor'])
