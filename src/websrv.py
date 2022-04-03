#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from flask import Flask, Blueprint, request, send_from_directory, render_template, session

from pprint import pprint

#from src.arc_patterns import ArcPatterns
from .cfg import Cfg
from .workspaces import Workspaces

from .helpers.installer import Installer
from .helpers.fs import FS
from .helpers.html import HTML
from .dia.universedia import UniverseDia

class WebSrv(object):
  def __init__ (self, fs: FS, verbose = 0):
    self.__fs = fs
    self.__verbose = verbose
    self.__settings = {}
    self.__settings['lang'] = os.environ.get('LANG')
    
    self.__blueprint = Blueprint('corp4_ide', __name__)
    self.__blueprint.add_url_rule('/', view_func=self.getIndex)
    
    self.__blueprint.add_url_rule('/settings', view_func=self.getSettings, methods=['GET'])
    self.__blueprint.add_url_rule('/settings', view_func=self.setSettings, methods=['POST'])
    
    self.__blueprint.add_url_rule('/static/<path:path>', view_func=self.getStatic, methods=['GET'])
    self.__blueprint.add_url_rule('/dia/<path:path>',    view_func=self.getDia,    methods=['GET'])
    
    self.__blueprint.add_url_rule('/workspace/<string:iw>',                                         view_func=self.getWorkspace,                methods=['GET'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/business_domains',                        view_func=self.getWorkspaceBusinessDomains, methods=['GET'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/business_domain/<string:businessDomain>', view_func=self.getWorkspaceBusinessDomain,  methods=['GET'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/tags',                                    view_func=self.getWorkspaceTags,            methods=['GET'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/tag/<string:tag>',                        view_func=self.getWorkspaceTag,             methods=['GET'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/systems',                                 view_func=self.getWorkspaceSystems,         methods=['GET'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/system/<string:system>',                  view_func=self.getWorkspaceSystem,          methods=['GET'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/links',                                   view_func=self.getWorkspaceLinks,           methods=['GET'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/solutions',                               view_func=self.getWorkspaceSolutions,       methods=['GET'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/sd/<string:sd>',                          view_func=self.getWorkspaceLinks,           methods=['GET'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/reports',                                 view_func=self.getWorkspaceReports,         methods=['GET'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/draw',                                    view_func=self.getWorkspaceDraw,            methods=['GET', 'POST'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/dia',                                     view_func=self.getWorkspaceDia,             methods=['GET'])
    
    self.__blueprint.add_url_rule('/legend',                             view_func=self.getHelpLegend,         methods=['GET'])
    self.__blueprint.add_url_rule('/patterns/<string:name>',             view_func=self.getHelpPatterns,       methods=['GET'])
    self.__blueprint.add_url_rule('/best_practices/<string:name>',       view_func=self.getHelpBestPractices,  methods=['GET'])
    self.__blueprint.add_url_rule('/api/workspace/<string:name>/reload', view_func=self.getWorkspaceReload,    methods=['POST'])

    self.__blueprint.add_url_rule('/workspace/<string:iw>/rfc/<string:rfc>/yaml/<string:filename>',          view_func=self.yaml,             methods=['GET', 'POST'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/rfc/<string:rfc>/yaml/<string:filename>/tree',     view_func=self.yamlTree,         methods=['GET', 'POST'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/rfc/<string:rfc>/yaml/<string:filename>/save',     view_func=self.setYamlSave,      methods=['POST'])
    self.__blueprint.add_url_rule('/workspace/<string:iw>/rfc/<string:rfc>/yaml/<string:filename>/saveexit', view_func=self.setYamlSaveExit,  methods=['POST'])

    self.__cfg = Cfg(verbose)
    self.__cfg.loadFromPath(self.__fs.getPathConfig())

    self.__workspaces = Workspaces(self.__fs, self.__cfg, self.__verbose)
    self.__workspaces.init()
    self.__workspaces.reload()

    self.__html = HTML(self.__fs, self.__verbose)
    self.__dia = UniverseDia(self.__fs, self.__html, self.__cfg, self.__verbose)

  def blueprint(self):
    return self.__blueprint

  def loadSettings(self, fullPath):
    try:
      with codecs.open(fullPath, 'r', encoding='utf-8') as stream:
        settings = yaml.safe_load(stream)
        self.__settings.update(settings)
        if self.__verbose > 7:
          print("DBG: Settings load %s" % fullPath)
    except yaml.YAMLError as exc:
      print("ERR: Bad format in %s: %s" % (fullPath, exc))

  def getSettings(self, lang):
    return render_template('html/settings.html', settings = self.__settings)

  def setSettings(self, lang):
    if request.method == 'POST':
      self.__settings['lang'] = request.form.get('lang', default='en', type=string)
      session['language'] = self.__settings['lang'] 
    return render_template('html/settings.html', settings = self.__settings)

  def getIndex(self):
    return render_template('html/index.html', workspaces = self.__cfg.getCfg('workspaces'))

  def getStatic(self, path):
    return send_from_directory(self.__fs.getPathHTML() + '/static/', path)

  def getDia(self, path):
    return send_from_directory(self.__fs.getPathHTML() + '/dia/', path)

  def getWorkspace(self, iw):
    workspace = self.__workspaces.getWorkspace(iw)
    return render_template('html/workspace.html', wsname = iw, 
                           workspaces = self.__cfg.getCfg('workspaces'),
                           workspace = workspace, workspace_stat = workspace.getStat())
    
  def getWorkspaceReload(self, iw):
    self.__workspaces.reload(iw)

  def getWorkspaceBusinessDomains(self, iw):
    workspace = self.__workspaces.getStat(iw)
    return render_template('html/business_domains.html', 
                              business_domains = self.__workspaces.getBusinessDomains(iw).getItems(),
                              wsname = iw, workspaces = self.__cfg.getCfg('workspaces'),
                              workspace = workspace)

  def getWorkspaceBusinessDomain(self, iw, businessDomain):
    workspace = self.__workspaces.getStat(iw)
    dm = self.__workspaces.getBusinessDomains(iw)
    #pprint(json.dumps(dm.getData()))
    bd = dm.getItem(businessDomain)
    pprint(json.dumps(bd))
    businessDomains, services, srvlinks = self.__workspaces.filterBusinessDomain(iw, businessDomain)
    pprint(json.dumps(services.getData()))
    self.__dia.drawBlockDiagram(businessDomain, iw, businessDomains, services, srvlinks, '%s/dia/%s/business-domain/%s' % (self.__fs.getPathHTML(), iw, businessDomain.replace('/', '-')))
    return render_template('html/business_domain.html', 
                              business_domain = bd,
                              business_domains = businessDomains.getItems(),
                              business_domain_services = services.getItems(),
                              business_domain_servicelinks = srvlinks.getItems(),
                              wsname = iw, workspaces = self.__cfg.getCfg('workspaces'),
                              workspace = workspace)

  def getWorkspaceTags(self, iw):
    workspace = self.__workspaces.getWorkspace(iw)
    return render_template('html/tags.html', wsname = iw, 
                           workspace = workspace,
                           tags = workspace.getTags().get().items(),
                           workspaces = self.__cfg.getCfg('workspaces'))

  def getWorkspaceTag(self, iw, tag):
    workspace = self.__workspaces.getWorkspace(iw)
    tags = workspace.getTags()
    tg = tags.getItem(tag)
    #domains, services, srvlinks = workspace.filterTag(iw, tg['id'], tg['id'])
    #self.__dia.drawBlockDiagram(tg['id'], iw, domains, services, srvlinks, '%s/dia/%s/tag/%s' % (self.__fs.getPathHTML(), iw, tg['id'].replace('/', '-')))
    
    return render_template('html/tag.html', 
                             wsname = iw, 
                             tag = tg,
                             #tag_servicelinks = srvlinks.items(),
                             #tag_services = services.items(),
                             workspaces = self.__cfg.getCfg('workspaces'),
                             workspace = workspace)

  def getWorkspaceSystems(self, iw):
    workspace = self.__workspaces.getWorkspace(iw)
    return render_template('html/systems.html', wsname = iw, 
                            systems = workspace.getSystems().get().items(),
                            workspaces = self.__cfg.getCfg('workspaces'), workspace = workspace)

  def getWorkspaceDia(self, iw):
    workspace = self.__workspaces.getWorkspace(iw)
    filename = ''
    mmd = ''
    fsystem = request.args.get('system')
    if fsystem is not None:
      fsystems, flinks = workspace.filterSystem(fsystem)
      filename = '%s/dia/%s/%s/%s' % (self.__fs.getPathHTML(), iw, 'system', fsystem)
      self.__dia.drawBlockDiagram(fsystem, {}, fsystems.get(), flinks.get(), filename)
    
    ftag = request.args.get('tag')
    pprint('--tag--')
    pprint(ftag)
    if ftag is not None:
      fsystems, flinks = workspace.filterTag(ftag)
      pprint(fsystems)
      filename = '%s/dia/%s/%s/%s' % (self.__fs.getPathHTML(), iw, 'tag', ftag)
      self.__dia.drawBlockDiagram(ftag, {}, fsystems.get(), flinks.get(), filename)
    f = open(filename + '.mmd')
    mmd  = f.read()
    f.close()
    return render_template('html/dia.html', wsname = iw, dia_scheme = mmd)

  def getWorkspaceSystem(self, iw, system):
    workspace = self.__workspaces.getWorkspace(iw)
    systems = workspace.getSystems()
    srv = systems.getItem(system)

    #fsystems, flinks = workspace.filterSystem(system)
    #self.__dia.drawBlockDiagram(system, iw, {}, fsystems.get(), flinks.get(), '%s/dia/%s/systems/%s' % (self.__fs.getPathHTML(), iw, system.replace('/', '-')))
    
    return render_template('html/system.html', wsname = iw, system = srv,
                            systems = systems.get().items(),
                            workspaces = self.__cfg.getCfg('workspaces'), workspace = workspace)

  def getWorkspaceSolutions(self, iw):
    workspace = self.__workspaces.getWorkspace(iw)
    return render_template('html/solutions.html', wsname = iw, 
                            #solutions = self.__workspaces.getWorkspace(iw).getSolutions().get(),
                            services = workspace.getServices().get(),
                            workspaces = self.__cfg.getCfg('workspaces'), workspace = workspace)


  def getWorkspaceLinks(self, iw):
    workspace = self.__workspaces.getWorkspace(iw).getStat()
    return render_template('html/links.html', wsname = iw, 
                            links = self.__workspaces.getWorkspace(iw).getLinks().get(),
                            workspaces = self.__cfg.getCfg('workspaces'), workspace = workspace)

  def workspace_sd(self, iw):
    workspace = self.__workspaces.getStat(iw)
    return render_template('html/links.html', wsname = iw, 
                            links = self.__workspaces.getLinks(iw).getItems(),
                            workspaces = self.__cfg.getCfg('workspaces'), workspace = workspace)

  def getHelpLegend(self):
    ap = ArcPatterns(self.__fs, self.__cfg.get(), self.__verbose)
    ap.makeAll()
    return render_template('html/help_legend.html', workspaces = self.__cfg.getCfg('workspaces'))

  def getHelpPatterns(self, name):
    return render_template('html/help_patterns.html', workspaces = self.__cfg.getCfg('workspaces'))

  def getHelpBestPractices(self, name):
    return render_template('html/help_best practices.html', workspaces = self.__cfg.getCfg('workspaces'))

  def getWorkspaceReports(self, iw):
    workspace = self.__workspaces.getStat(iw)
    return render_template('html/reports.html', wsname = iw, workspaces = self.__cfg.getCfg('workspaces'))

  def getWorkspaceDraw(self, iw):
    workspace = self.__workspaces.getStat(iw)
    return render_template('html/draw.html', wsname = iw, workspaces = self.__cfg.getCfg('workspaces'))

  def yaml(self, iw, rfc, filename):
      """Renders index page to edit provided yaml file."""
      workspace = self.__workspaces.getStat(iw)
      fn = self.__fs.getPathData() + filename
      data = ''
      try:
        with open(fn) as file_obj:
          data = yaml.load(file_obj, Loader=yaml.Loader)
      except Exception as e:
        print("ERR: YAML: %s: %s" % (fn, str(e)))

      workspace = self.__workspaces.getStat(iw)
      services = self.__workspaces.getServices(iw)
      links = self.__workspaces.getLinks(iw)
      
      self.dia.drawBlockDiagram(rfc, iw, domains, services, links, '%s/dia/%s/rfc/%s' % (self.__fs.getPathHTML(), iw, rfc.replace('/', '-')))

      return render_template('html/yaml.html',
                             data=json.dumps(data),
                             change_str='') # app.config['STRING_TO_CHANGE'])

  def yamlTree(self, iw, rfc, filename):
      workspace = self.__workspaces.getStat(iw)
      fn = self.__fs.getPathData() + filename
      data = ''
      try:
        with open(fn) as file_obj:
          data = yaml.load(file_obj, Loader=yaml.Loader)
      except Exception as e:
        print("ERR: YAML: %s: %s" % (fn, str(e)))
      return render_template('html/treeyaml.html',
                             data=data, datastr=json.dumps(data),
                             change_str='') # app.config['STRING_TO_CHANGE'])

  def setYamlSave(self, iw, rfc, filename):
      out = request.json.get('yaml_data')
      fn = self.__fs.getPathData() + filename
      data = ''
      try:
        with open(fn, 'w') as file_obj:
          yaml.dump(out, file_obj, default_flow_style=False)
      except Exception as e:
        print("ERR: YAML: %s: %s" % (fn, str(e)))
      return "Data saved successfully!"

  def setYamlSaveExit(self, iw, rfc, filename):
      fn = self.__fs.getPathData() + filename
      out = request.json.get('yaml_data')
      data = ''
      try:
        with open(fn, 'w') as file_obj:
            yaml.dump(out, file_obj, default_flow_style=False)
      except Exception as e:
        print("ERR: YAML: %s: %s" % (fn, str(e)))
      func = request.environ.get('werkzeug.server.shutdown')
      if func:
          func()
      return "Saved successfully, Shutting down app! You may close the tab!"

