#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import docker
from pprint import pprint

class MermaidCLI():
  def __init__ (self, verbose = 0):
    self.__verbose = verbose
    self.__docker = None
    self.__src = 'minlag/mermaid-cli'
    try:
      self.__docker = docker.from_env()
      info = self.__docker.version()
      if self.__verbose > 5:
        print("DBG: docker.version %s" % (info['Components'][0]['Version']))
    except:
      print("FATAL: Docker Not Found")

  def makePNG(self, pathDia, filename, width = 3000):
    # HELP: https://docker-py.readthedocs.io/en/stable/containers.html
    # HELP: https://github.com/mermaid-js/mermaid-cli
    # docker run -it -v /path/to/diagrams:/data minlag/mermaid-cli -i /data/diagram.mmd

    if not self.__docker:
      return False

    fname = filename.replace(pathDia, '')
    command = '-i /data/%s -o /data/%s.png -w %d' % (fname, fname, width)

    # Volumes
    volumes = dict()
    volumes[os.path.abspath(pathDia)] = {'bind': '/data'}

    try:
      if self.__verbose > 5:
        print("DBG: Docker: Run '%s' container. Command: %s" % (self.__src, command))
      container = self.__docker.containers.run(self.src, command=command, volumes=volumes, detach=False, user='root', auto_remove=True)

      if self.__verbose > 5:
        print("DBG: %s" % container)

    except Exception as e:
      print("FATAL: Docker run container '%s': %s" % (self.__src, str(e)))
      return False

    return True

