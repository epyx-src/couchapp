# -*- coding: utf-8 -*-
#
# Copyright 2008,2009 Alexander Lang (alex@upstre.am), Frank Prößdorf (fp@notjusthosting.com)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at#
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import glob
import re
import os
import sys
import json

from couchapp import pystache
from couchapp.inflector.Inflector import Inflector

class ResourceGenerator(object):
    template_dir = ''
    
    def __init__(self, template_dir, ui):
        self.cli = Cli(sys.stdin, sys.stdout)
        self.ui = ui
        self.inflector = Inflector()
        pystache.Template.ctag = '%>'
        pystache.Template.otag = '<%'
        self.template_dir = template_dir
        
    def generate(self, path, name, options):
        """ Generates a complete CRUD app for a given 
        resource name.

        :attr path: path to the application        
        :attr name: singular name with underscore of the resource 
            to create, e.g. blog_post
        :attr options: must contain the attributes for the resource 
            as a string, separated by commas, e.g. 
            {'attributes': 'title,author,body'}
        """
        if options['attributes'] == '':
            self.cli.tell('No attributes given. Please add --attributes att1,att2...')
            return
            
        view = self.prepare_view(name, options['attributes'])

        for template_path in self.templates():
            in_app_path_template = template_path.replace(
                            self.template_dir + '/', '')
            in_app_path = pystache.render(in_app_path_template, view)
            if os.path.isdir(template_path):
                self.process_directory(path, in_app_path)
            else:
                self.process_file(template_path, view, path, in_app_path)
        self.generate_apprc(path)
    
    def templates(self):
        """ Fetch all the available templates 
        from sub-directories recursively """
        return glob.glob(os.path.join(self.template_dir, '*', '*')) + \
            glob.glob(os.path.join(self.template_dir, '*', '*', '*'))

    def process_file(self, template_path, view, path, 
                in_app_path):
        """ Update the contents of template_path 
        with the given template and view """
        template = self.ui.read(template_path)
        contents = pystache.render(template, view)
        dpath = os.path.join(path, os.path.dirname(in_app_path)
        if not os.path.exists(dpath):
            os.makedirs(dpath)

        fpath = os.path.join(path, in_app_path)
        if os.path.exists(fpath) and not \
                self.cli.ask("really overwrite %s?" % in_app_path):
            self.cli.tell("skipping %s." % in_app_path)
        else:
            self.cli.tell("creating %s." % in_app_path)
            self.ui.write(fpath, contents)
    
    def prepare_view(self, name, attributes):
        """ Create a hash that enables us to 
        render the mustache templates """
        plural_name = self.inflector.pluralize(name)
        view = {
            'plural_name': plural_name, 'singular_name': name,
            'plural_label': self.inflector.titleize(plural_name),
            'singular_label': self.inflector.titleize(name),
            'app_name': self.app_name()
        }
        attributes_view = map(self.create_attribute, attributes.split(','))
        for attribute in attributes_view:
            attribute['singular_name'] = name
            attribute['plural_name'] = plural_name
        view['attributes'] = attributes_view
        view['first_attribute'] = [attributes_view[0]]
        return view
        

    def create_attribute(self, attribute):
        """ Create a hash describing the attribute """
        return {
            'name': attribute,
            'label': attribute.capitalize(),
            'class': attribute
        }
        
    def process_directory(self, path, in_app_path):
        dest = os.path.join(path, in_app_path)
        if os.path.exists(dest):
            self.cli.tell("creating %s." % in_app_path)
            os.makedirs(os.path.join(path, in_app_path))
            print "creating"
        else:
            self.cli.tell("skipping %s. exists." % in_app_path)

    def generate_apprc(self, app_path):
        rcpath = os.path.join(app_path, '.couchapprc')
        if os.path.isfile(rcpath):
            conf = self.ui.read_json(rcpath)
        else:
            conf = {'env': {}}
        
        if conf.get('env') == None or 'db' not in conf['env'].get('test', {}):
             conf['env']['test'] = { 
                'db': 'http://localhost:5984/%s_test/' % self.app_name()
             }
        self.ui.write_json(rcpath, conf)

    def app_name(self):
        return self.ui.get_app_name(None, None)
        
class Cli(object):
    def __init__(self, _in, _out):
        self.inIO = _in
        self.outIO = _out
        
    def ask(self, question):
        self.outIO.write(question + " [y/n]: ")
        answer = self.inIO.readline()
        if answer == "y\n":
            return True
        elif answer == "n\n":
            return False
        else:
            self.ask(question)
    
    def tell(self, statement):
        self.outIO.write(statement + "\n")