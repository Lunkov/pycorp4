#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import docker

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

    if self.docker:
      print("ERR: Docker run: Not Found")
      return False
    
    command = '-i /data/%s.mmd' % filename

    # Volumes
    volumes = dict()
    volumes[os.path.abspath(pathDia)] = {'bind': '/data'}

    try:
      if self.verbose:
        print("LOG: Docker: Run '%s' container" % self.containerName)
      container = self.docker.containers.run(self.src, command=command, volumes=volumes, detach=False)

    except Exception as e:
      print("FATAL: Docker run container '%s': %s" % (self.src, str(e)))
      return False
      
    return True

