#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import optparse

from src.fs import FS
from src.architector import Architector


class CommandArgs(object):
  ''' Class For Set Default Command Line Arguments '''

  def __init__(self, commandfile):
    ''' Constructor '''
    usage = commandfile+' [--help][-m module]'
    self.parser = optparse.OptionParser(usage, add_help_option=False)
    self.parser.add_option('-h', '--help',
                           action="store_true",
                           help="show this help message and exit",
                           dest="help"
                          )
    self.parser.add_option('-p', '--path',
                           type="string",
                           help="Data path",
                           dest="path"
                          )
    self.parser.add_option('-x', '--xls',
                           type="string",
                           help="load data from XLS",
                           dest="xls"
                          )
    self.parser.add_option('-u', '--update',
                           help="Load/update online data",
                           action="store_true",
                           dest="update",
                           default=False
                          )
    self.parser.add_option('-t', '--templates',
                           help="Path to templates",
                           type="string",
                           dest="templates",
                           default="templates"
                          )
    self.parser.add_option('-a', '--analyze',
                           help="Analyze data",
                           action="store_true",
                           dest="analyze",
                           default=False
                          )
    self.parser.add_option('-o', '--out',
                           help="Path for save results",
                           dest="out",
                           type="string",
                           default="html"
                          )
    self.parser.add_option('-v', '--verbose',
                           help="Verbose",
                           type="int",
                           dest="verbose",
                           default=0
                          )
    self.options = None

  def get_parser(self):
    ''' Get Parser '''
    return self.parser

  def get_options(self):
    ''' Get Options '''
    return self.options

  def print_info(self):
    ''' Print Help '''
    self.options, _remainder = self.parser.parse_args()
    if self.options.help:
      self.parser.print_help()
      sys.exit(os.EX_CONFIG)

def main(options):
  ''' Main Function '''
  fs = FS(options.verbose)
  
  if options.path:
    fs.setPathData(options.path)
  if options.templates:
    fs.setPathTemplates(options.templates)
  if options.out:
    fs.setPathHTML(options.out)

  arc = Architector(fs, options.verbose)
  if options.xls:
    arc.readXLS(options.xls)

  if options.path:
    arc.readXLSs(options.path)

  if options.update:
    arc.updateOnlineData()
  
  if options.path:
    arc.loadData()

  arc.prepare()
  
  if options.analyze:
    arc.analyze()

  if options.out:
    arc.makeAll()

if __name__ == '__main__':
  ARGS = CommandArgs(os.path.basename(__file__))
  ARGS.print_info()
  main(ARGS.get_options())
