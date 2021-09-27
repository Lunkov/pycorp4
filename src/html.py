#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs

class HTML():
  def __init__ (self):
    self.header = """<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-KyZXEAg3QhqLMpG8r+8fhAXLRk2vvoC2f3B09zVXn8CA5QIVfZOJ3BCsw2P0p/We" crossorigin="anonymous">
                   <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-U1DAWAznBHeqEIlVSCgzq+c9gqGAJn5c/t99JyeKa9xxaYpSvHU5awsuZVVFIhvj" crossorigin="anonymous"></script>"""
    self.navbar = """<nav class="navbar navbar-light bg-light">
                      <div class="container-fluid">
                        <a class="navbar-brand" href="/">Arc</a>
                      </div>
                    </nav>"""

  def save(self, filename, content):
    file = codecs.open("out/%s.html" % filename, 'w', 'utf-8')
    file.write(self.header)
    file.write(self.navbar)
    file.write('<div class="container">')
    file.write(content)
    file.write('</div>')
    file.close()
