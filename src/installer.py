#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

class Installer():
  def __init__ (self, fs, options):
    self.fs = fs
    self.options = options
    self.verbose = options.verbose

  def update(self):
    self.fs.mkDir(self.options.webpath + '/%s',
                   ['static'])
    
    self.fs.rsync(self.options.templates + '/static/%s', self.options.webpath + '/static/%s', ['js', 'css', 'scss', 'vendor'])
