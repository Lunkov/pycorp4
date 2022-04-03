#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import logging
import os
import re
import hashlib
import sysrsync
import tempfile


class FS():
  def __init__ (self, config = 'etc/', templates = 'tempaltes/', datapath = 'data/', webpath = 'www/', verbose = 0):
    self.__verbose = verbose
    self.__pathHTML = webpath
    self.__pathData = datapath
    self.__pathTemplates = templates
    self.__pathConfig = config
    self.__cnt_files = 0
    self.__cnt_writes = 0

  def initCount(self):
    self.__cnt_files = 0
    self.__cnt_writes = 0

  def setPathConfig(self, p):
    self.__pathConfig = p

  def getPathConfig(self):
    return self.__pathConfig

  def setPathHTML(self, p):
    self.__pathHTML = p

  def getPathHTML(self):
    return self.__pathHTML

  def setPathData(self, p):
    self.__pathData = p

  def getPathData(self):
    return self.__pathData

  def setPathTemplates(self, p):
    self.__pathTemplates = p

  def getPathTemplates(self):
    return self.__pathTemplates

  def getPathTempDir(self):
    return tempfile.gettempdir()

  def md5File(self, fname):
    hash_md5 = hashlib.md5()
    try:
      with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
          hash_md5.update(chunk)
    except:
      return '-'
    return hash_md5.hexdigest()

  def md5String(self, data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()

  def writeFile(self, fname, data):
    self.__cnt_files = self.__cnt_files + 1
    if self.md5String(data) == self.md5File(fname):
      return False
    if self.__verbose:
      print("LOG: Write file: %s" % fname)
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    text_file = codecs.open(fname, 'w', 'utf-8')
    text_file.write(data)
    text_file.close()
    self.__cnt_writes = self.__cnt_writes + 1
    return True

  def mkDir(self, destination, dirs):
    for p in dirs:
      os.makedirs(destination % p, exist_ok=True)
      
  def rsync(self, source, destination, dirs):
    for p in dirs:
      if os.name != 'nt':
        if os.path.exists(source % p): 
          sysrsync.run(source = source % p,
                     destination = destination % p,
                     sync_source_contents = True,
                     exclusions = ['.~*', 'Thumbs.db:encryptable'],
                     options = ['-a'],
                     verbose = self.__verbose)
        else:
          print("ERR: Path is not exists: %s" % (source % p))

  def printStats(self):
    if self.__verbose > 3:
      print("LOG: Write files: %d / %d" % (self.cnt_writes, self.cnt_files))

  @staticmethod
  def rm(pathName):
    """ remove folders
    """
    shutil.rmtree(pathName, ignore_errors=True)
    mypath = Path(pathName)
    if mypath.is_dir():
      for root, dirs, files in os.walk(pathName):
        for f in files:
          try:
            os.chmod(os.path.join(root, f),stat.S_IRUSR|stat.S_IRGRP|stat.S_IROTH|stat.S_IXUSR|stat.S_IRUSR|stat.S_IWUSR|stat.S_IWGRP|stat.S_IXGRP)
          except:
            continue
          os.remove(os.path.join(root, f))
        for d in dirs:
          shutil.rmtree(os.path.join(root, d), ignore_errors=True)
      for f in os.scandir(pathName):
        try:
          if f.is_dir():
            shutil.rmtree(f, ignore_errors=True)
          if f.is_file():
            os.remove(f)
        except:
          continue