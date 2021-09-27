#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import optparse

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
    self.parser.add_option('-o', '--out',
                           help="Path for save results",
                           dest="out",
                           type="string",
                           default="html"
                          )
    self.parser.add_option('-v', '--verbose',
                           help="Verbose",
                           action="store_true",
                           dest="verbose",
                           default=False
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
  arc = Architector(options.verbose)
  if options.xls:
    arc.readXLS(options.xls)
  
  if options.update:
    arc.updateOnlineData()

  if options.out:
    arc.makeAll(options.out)

if __name__ == '__main__':
  ARGS = CommandArgs(os.path.basename(__file__))
  ARGS.print_info()
  main(ARGS.get_options())
