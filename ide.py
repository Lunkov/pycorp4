#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import optparse
from flask import Flask, Blueprint, request, send_from_directory, render_template

from pprint import pprint

from src.installer import Installer
from src.fs import FS
from src.cfg import Cfg
from src.arc_patterns import ArcPatterns
from src.workspaces import Workspaces

from src.fabricdia import FabricDia
from src.html import HTML

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
    self.parser.add_option('-c', '--config',
                           type="string",
                           help="Config path",
                           dest="config",
                           default="etc/"
                          )
    self.parser.add_option('-p', '--path',
                           type="string",
                           help="Data path",
                           default="workspaces/",
                           dest="datapath"
                          )
    self.parser.add_option('-w', '--webpath',
                           type="string",
                           help="Web path",
                           default="web/",
                           dest="webpath"
                          )
    self.parser.add_option('-t', '--templates',
                           help="Path to templates",
                           type="string",
                           dest="templates",
                           default="templates/"
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

class WebSrv(object):
  def __init__ (self, fs, options):
    self.fs = fs
    self.options = options
    self.blueprint = Blueprint('corp4_ide', __name__)
    self.blueprint.add_url_rule('/', view_func=self.index)
    self.blueprint.add_url_rule('/static/<path:path>', view_func=self.static)
    self.blueprint.add_url_rule('/dia/<path:path>', view_func=self.dia)
    self.blueprint.add_url_rule('/workspace/<string:iw>', view_func=self.workspace)
    self.blueprint.add_url_rule('/workspace/<string:iw>/domains', view_func=self.workspace_domains)
    self.blueprint.add_url_rule('/workspace/<string:iw>/domain/<string:domain>', view_func=self.workspace_domain)
    self.blueprint.add_url_rule('/workspace/<string:iw>/tags', view_func=self.workspace_tags)
    self.blueprint.add_url_rule('/workspace/<string:iw>/tag/<string:tag>', view_func=self.workspace_tag)
    self.blueprint.add_url_rule('/workspace/<string:iw>/services', view_func=self.workspace_services)
    self.blueprint.add_url_rule('/workspace/<string:iw>/service/<string:service>', view_func=self.workspace_service)
    self.blueprint.add_url_rule('/workspace/<string:iw>/links', view_func=self.workspace_links)
    self.blueprint.add_url_rule('/legend', view_func=self.help_legend)
    self.blueprint.add_url_rule('/patterns/<string:name>', view_func=self.help_patterns)
    self.blueprint.add_url_rule('/best_practices/<string:name>', view_func=self.help_best_practices)
    self.blueprint.add_url_rule('/api/workspace/<string:name>/reload', view_func=self.workspace_reload, methods=['POST'])
    self.cfg = Cfg(options.verbose)
    self.cfg.loadFromPath(options.config)
    self.workspaces = Workspaces(fs, self.cfg, options.verbose)
    self.workspaces.loads()
    self.html = HTML(self.fs, options.verbose)
    self.dia = FabricDia(self.fs, self.html, self.cfg, options.verbose)

  def index(self):
    return render_template('html/index.html', options = self.options, workspaces = self.cfg.getCfg('workspaces'))

  def static(self, path):
    return send_from_directory(options.webpath + '/static/', path)

  def dia(self, path):
    return send_from_directory(options.webpath + '/dia/', path)

  def workspace(self, iw):
    workspace = self.workspaces.getStat(iw)
    return render_template('html/workspace.html', options = self.options, wsname = iw, 
                           workspaces = self.cfg.getCfg('workspaces'), workspace = workspace)
    
  def workspace_reload(self, iw):
    self.workspaces.reload(iw)

  def workspace_domains(self, iw):
    workspace = self.workspaces.getStat(iw)
    return render_template('html/domains.html', options = self.options,
                              domains = self.workspaces.getDomains(iw).getItems(),
                              wsname = iw, workspaces = self.cfg.getCfg('workspaces'),
                              workspace = workspace)

  def workspace_domain(self, iw, domain):
    workspace = self.workspaces.getStat(iw)
    dm = self.workspaces.getDomains(domain)
    domains, services, srvlinks = self.workspaces.filterDomain(iw, domain)
    self.dia.drawBlockDiagram(domain, iw, domains, services, srvlinks, '%s/dia/%s/domain/%s' % (self.fs.getPathHTML(), iw, domain.replace('/', '-')))
    return render_template('html/domain.html', options = self.options,
                              domain = dm,
                              domains = domains.getItems(),
                              domain_services = services.getItems(),
                              domain_servicelinks = srvlinks.getItems(),
                              wsname = iw, workspaces = self.cfg.getCfg('workspaces'),
                              workspace = workspace)

  def workspace_tags(self, iw):
    workspace = self.workspaces.getStat(iw)
    return render_template('html/tags.html', options = self.options, wsname = iw, 
                           tags = self.workspaces.getTags(iw).getItems(),
                           workspaces = self.cfg.getCfg('workspaces'), workspace = workspace)

  def workspace_tag(self, iw, tag):
    workspace = self.workspaces.getStat(iw)
    tags = self.workspaces.getTags(iw)
    tg = tags.getItem(tag)
    domains, services, srvlinks = self.workspaces.filterTag(iw, tg['id'], tg['id'])
    self.dia.drawBlockDiagram(tg['id'], iw, domains, services, srvlinks, '%s/dia/%s/tag/%s' % (self.fs.getPathHTML(), iw, tg['id'].replace('/', '-')))
    
    return render_template('html/tag.html', options = self.options,
                             wsname = iw, 
                             tag = tg,
                             tag_servicelinks = srvlinks.items(),
                             tag_services = services.items(),
                             workspaces = self.cfg.getCfg('workspaces'),
                             workspace = workspace)

  def workspace_services(self, iw):
    workspace = self.workspaces.getStat(iw)
    return render_template('html/services.html', options = self.options, wsname = iw, 
                            services = self.workspaces.getServices(iw).getItems(),
                            workspaces = self.cfg.getCfg('workspaces'), workspace = workspace)

  def workspace_service(self, iw, service):
    workspace = self.workspaces.getStat(iw)
    services = self.workspaces.getServices(iw)
    srv = services.getItem(service)
    return render_template('html/service.html', options = self.options, wsname = iw, service = srv,
                            services = self.workspaces.getServices(iw).getItems(),
                            workspaces = self.cfg.getCfg('workspaces'), workspace = workspace)

  def workspace_links(self, iw):
    workspace = self.workspaces.getStat(iw)
    return render_template('html/links.html', options = self.options, wsname = iw, 
                            links = self.workspaces.getLinks(iw).getItems(),
                            workspaces = self.cfg.getCfg('workspaces'), workspace = workspace)

  def help_legend(self):
    ap = ArcPatterns(self.fs, self.cfg.get(), self.options.verbose)
    ap.makeAll()
    return render_template('html/help_legend.html', options = self.options, workspaces = self.cfg.getCfg('workspaces'))

  def help_patterns(self, name):
    return render_template('html/help_patterns.html', options = self.options, workspaces = self.cfg.getCfg('workspaces'))

  def help_best_practices(self, name):
    return render_template('html/help_best practices.html', options = self.options, workspaces = self.cfg.getCfg('workspaces'))

if __name__ == "__main__":
  ARGS = CommandArgs(os.path.basename(__file__))
  ARGS.print_info()
  
  options = ARGS.get_options()
  fs = FS(options)
  i = Installer(fs, options)
  i.update()
  
  webs = WebSrv(fs, options)

  app = Flask(__name__, static_folder = options.webpath, template_folder = options.templates)
  app.register_blueprint(webs.blueprint)

  app.run(debug = (options.verbose > 7))
