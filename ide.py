#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import optparse
from flask import Flask, Blueprint, request, send_from_directory, render_template, session

from src.cfg import Cfg
from src.websrv import WebSrv
from src.helpers.installer import Installer
from src.helpers.fs import FS

class CommandArgs(object):
  ''' Class For Set Default Command Line Arguments '''

  def __init__(self, commandfile):
    ''' Constructor '''
    usage = commandfile+' [--help][-m module]'
    self.__parser = optparse.OptionParser(usage, add_help_option = False)
    self.__parser.add_option('-h', '--help',
                           action="store_true",
                           help="show this help message and exit",
                           dest="help"
                          )
    self.__parser.add_option('-c', '--config',
                           type="string",
                           help="Config path",
                           dest="config",
                           default="etc/"
                          )
    self.__parser.add_option('-p', '--datapath',
                           type="string",
                           help="Data path",
                           default="workspaces/",
                           dest="datapath"
                          )
    self.__parser.add_option('-w', '--webpath',
                           type="string",
                           help="Web path",
                           default="web/",
                           dest="webpath"
                          )
    self.__parser.add_option('-t', '--templates',
                           help="Path to templates",
                           type="string",
                           dest="templates",
                           default="templates/"
                          )
    self.__parser.add_option('-v', '--verbose',
                           help="Verbose",
                           type="int",
                           dest="verbose",
                           default=0
                          )
    self.__options = None

  def getParser(self):
    ''' Get Parser '''
    return self.__parser

  def getOptions(self):
    ''' Get Options '''
    return self.__options

  def printInfo(self):
    ''' Print Help '''
    self.__options, _remainder = self.__parser.parse_args()
    if self.__options.help:
      self.__parser.print_help()
      sys.exit(os.EX_CONFIG)

if __name__ == "__main__":
  ARGS = CommandArgs(os.path.basename(__file__))
  ARGS.printInfo()

  options = ARGS.getOptions()
  fs = FS(options.config, options.templates, options.datapath, options.webpath, options.verbose)
  i = Installer(fs, options.verbose)
  i.update()

  webs = WebSrv(fs, options.verbose)

  app = Flask(__name__, static_folder = options.webpath, template_folder = options.templates)
  app.register_blueprint(webs.blueprint())
  app.secret_key = 'super secret key'
  app.config['SESSION_TYPE'] = 'filesystem'

  app.run(debug = (options.verbose > 7))
