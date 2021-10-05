#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import logging
import os
import re
import hashlib
import jinja2
import sysrsync


class FS():
  def __init__ (self, verbose):
    self.verbose = verbose
    self.cnt_files = 0
    self.cnt_writes = 0

  def md5File(self, fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
      for chunk in iter(lambda: f.read(4096), b""):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()

  def md5String(self, data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()

  def writeFile(self, fname, data):
    self.cnt_files = self.cnt_files + 1
    if self.md5String(data) == self.md5File(fname):
      return False
    text_file = codecs.open(fname, 'w', 'utf-8')
    text_file.write(data)
    text_file.close()
    self.cnt_writes = self.cnt_writes + 1
    return True

  def mkDir(self, destination, dirs):
    for p in dirs:
      os.makedirs(destination % p, exist_ok=True)

  def rsync(self, source, destination, dirs):
    for p in dirs:
      if os.name != 'nt':
        sysrsync.run(source = source % p,
                   destination = destination % p,
                   sync_source_contents = True,
                   exclusions = ['.~*', 'Thumbs.db:encryptable'],
                   options = ['-a'],
                   verbose = self.verbose)

  def printStats(self):
    if self.verbose:
      print("LOG: Write files: %d / %d" % (self.cnt_writes, self.cnt_files))
