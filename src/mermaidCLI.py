#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import docker
from pprint import pprint

class MermaidCLI():
  def __init__ (self, verbose):
    self.verbose = verbose
    self.docker = None
    self.src = 'minlag/mermaid-cli'
    try:
      self.docker = docker.from_env()
      info = self.docker.version()
      if self.verbose:
        print("DBG: docker.version %s" % (info['Components'][0]['Version']))
    except:
      print("FATAL: Docker Not Found")

  def makePNG(self, pathDia, filename):
    # HELP: https://docker-py.readthedocs.io/en/stable/containers.html
    # HELP: https://github.com/mermaid-js/mermaid-cli
    # docker run -it -v /path/to/diagrams:/data minlag/mermaid-cli -i /data/diagram.mmd

    if not self.docker:
      print("ERR: Docker run: Not Found")
      return False
    
    fname = filename.replace(pathDia, '')
    command = '-i /data/%s -o /data/%s.png' % (fname, fname)

    # Volumes
    volumes = dict()
    volumes[os.path.abspath(pathDia)] = {'bind': '/data'}
    pprint(pathDia)
    pprint(volumes)

    try:
      if self.verbose:
        print("LOG: Docker: Run '%s' container. Command: %s" % (self.src, command))
      container = self.docker.containers.run(self.src, command=command, volumes=volumes, detach=False, user='root', auto_remove=True)
      
      print("LOG: %s" % container)

    except Exception as e:
      print("FATAL: Docker run container '%s': %s" % (self.src, str(e)))
      return False
      
    return True

