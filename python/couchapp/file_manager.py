#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Benoit Chesneau <benoitc@e-engura.org>
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
#

from glob import glob
from mimetypes import guess_type
import os
import shutil
import sys
import urlparse
import urllib

# compatibility with python 2.4
try:
    from hashlib import md5 as _md5
except ImportError:
    import md5
    _md5 = md5.new

try:
    import simplejson as json
except ImportError:
    import json # Python 2.6


from couchdb import Server, ResourceNotFound

__all__ = ['DEFAULT_SERVER_URI', 'FileManager']

DEFAULT_SERVER_URI = 'http://127.0.0.1:5984/'

def write_json(filename, content):
    f = open(filename, 'w')
    f.write(json.dumps(content))
    f.close()

def read_json(filename):
    try:
        f = file(filename, 'r')
        
    except IOError, e:
        if e[0] == 2:
            return {}
        raise
    data = json.loads(f.read())
    f.close()
    return data


def parse_uri(string):
    parts = urlparse.urlsplit(urllib.unquote(string))
    if parts[0] != 'http' and parts[0] != 'https':
        raise ValueError('Invalid dbstring')
     
    path = parts[2].strip('/').split('/')

    dbname = ''
    docid = ''
    if len(path) >= 1:
        db_parts=[]
        i = 0
        while 1:
            try:
                p = path[i]
            except IndexError:
                break

            if p == '_design': break
            db_parts.append(p)
            i = i + 1
        dbname = '/'.join(db_parts)
        
        if i < len(path) - 1:
            docid = '/'.join(path[i:])

    server_uri = '%s://%s' % (parts[0], parts[1])
    return server_uri, dbname, docid

def get_appname(docid):
    return docid.split('_design/')[1]


def sign_file(file_path):
    if os.path.isfile(file_path):
        f = open(file_path, 'rb')
        content = f.read()
        f.close()
        return _md5(content).hexdigest()
    return ''

class FileManager(object):
    
    def __init__(self, dbstring, app_dir='.'):
        self.app_dir = app_dir 

        # load conf
        self.conf = self.load_metadata(app_dir)
        
        # init default
        self.get_default()

        if not dbstring or not "/" in dbstring:
            
            if dbstring:
                self.db_name = dbstring
            else: 
                if self.default_dbname:
                    self.db_name = self.default_dbname
                else:
                    raise ValueError("database isn't specified")

            self.server_uri = self.default_server
        else:
            self.server_uri, self.db_name, docid = parse_uri(dbstring)

        self.couchdb_server = Server(self.server_uri)

        # create db if it don't exist
        try:
            self.db = self.couchdb_server.create(self.db_name)
        except: # db already exist
            self.db = self.couchdb_server[self.db_name]

    @classmethod
    def generate_app(cls, app_dir):
        template_dir = os.path.normpath(os.path.join(os.path.dirname(__file__),
                '../app-template'))
        shutil.copytree(template_dir, app_dir)
        cls.init(app_dir)

    @classmethod
    def init(cls, app_dir):
        if not os.path.isdir(app_dir):
            print>>sys.stderr, "%s don't exist" % app_dir
            return
        metadata_dir = '%s/.couchapp' % app_dir
        if not os.path.isdir(metadata_dir):
            os.makedirs(metadata_dir)
            write_json('%s/rc.json' % metadata_dir, {})
        else:
            print>>sys.stderr, "couchapp already initialized"

    def load_metadata(self, app_dir):
        rc_file = '%s/.couchapp/rc.json' % app_dir
        if os.path.isfile(rc_file):
            self.conf = read_json(rc_file)

    def get_default(self):
        if not self.conf:
            self.load_metadata(self.app_dir)
        if self.conf and 'default' in self.conf:
            default = self.conf['default']
            self.default_server = default.get('server',
                DEFAULT_SERVER_URI)
            self.default_dbname = default.get('dbname')
            return
        self.default_server = DEFAULT_SERVER_URI
        self.default_dbname = ''


    def push_app(self, app_dir, app_name):
        docid = '_design/%s' % app_name

        attach_dir = os.path.join(app_dir, '_attachments')

        doc = self.dir_to_fields(app_dir)

        if docid in self.db:
            design = self.db[docid]

            doc.update({
                    '_id': docid,
                    '_rev': design['_rev'],
                    'signatures': design.get('signatures', {}),
                    '_attachments': design['_attachments']
            })
        
        self.db[docid] = doc 

        self.push_directory(attach_dir, docid)

    @classmethod
    def clone(cls, app_uri, app_dir):
        
        server_uri, db_name, docid = parse_uri(app_uri) 
        
        couchdb_server = Server(server_uri)
        try:
            db = couchdb_server.create(db_name)
        except: # db already exist
            db = couchdb_server[db_name]
 
        app_name = get_appname(docid)
        if not app_dir:
            app_dir = os.path.normpath(os.path.join(os.getcwd(), app_name))

        if not os.path.isdir(app_dir):
            os.makedirs(app_dir)
        
        design = db[docid]

        signatures = design.get('signatures', {})


        print "sign %s " % signatures
        # get views and show
        for vs in ['views', 'show']:
            if vs in design:
                vs_dir = os.path.join(app_dir, vs)
                if not os.path.isdir(vs_dir):
                    os.makedirs(vs_dir)

                for vsname, vs_item in design[vs].iteritems():
                    vs_item_dir = os.path.join(vs_dir, vsname)
                    if not os.path.isdir(vs_item_dir):
                        os.makedirs(vs_item_dir)
    
                    for func_name, func in vs_item.iteritems():
                        filename = os.path.join(vs_item_dir, '%s.js' %
                            func_name)
                        open(filename, 'w').write(func)

        # get attachments
        if '_attachments' in design:
            attach_dir = os.path.join(app_dir, '_attachments')
            if not os.path.isdir(attach_dir):
                os.makedirs(attach_dir)
            for filename in design['_attachments'].iterkeys():
                file_path = os.path.join(attach_dir, filename)
                current_dir = os.path.dirname(file_path)
                if not os.path.isdir(current_dir):
                    os.makedirs(current_dir)
        
                if signatures.get(filename) != sign_file(file_path):
                    content = db.get_attachment(docid, filename)
                    f = open(file_path, 'wb')
                    f.write(content)
                    f.close()

        


    def _load_file(self, fname):
        f = file(fname, 'r')
        data = f.read()
        f.close
        return data

    def dir_to_fields(self, app_dir, depth=0):
        fields={}
        for name in os.listdir(app_dir):
            current_path = os.path.join(app_dir, name)
            if name.startswith('.'):
                continue
            elif depth == 0 and name.startswith('_'):
                continue
            elif os.path.isdir(current_path):
                fields[name] = self.dir_to_fields(current_path,
                        depth=depth+1)
            else:
                content = self._load_file(current_path)
                if name.endswith('.json'):
                    fields[name[:-5]] = json.loads(content)
                elif name.endswith('.js'):
                    fields[name[:-3]] = content
                else:
                    fields[name] = content
        return fields
    
    def push_directory(self, attach_dir, docid):
        # get attachments
        signatures = {}
        attachments = {}
        for root, dirs, files in os.walk(attach_dir):
            if files:
                for filename in files:
                    file_path = os.path.join(root, filename)
                    
                    name = file_path.split('%s/' % attach_dir)[1] 
                    signature = sign_file(file_path)
                    signatures[name] = signature
                    attachments[name] = file
        
        # detect attachments to be removed and keep
        # only new version attachments to update.
        design = self.db[docid]
        if 'signatures' in design:
            for filename in design['signatures'].iterkeys():
                if filename not in signatures:
                    self.db.delete_attachment(design, filename)
                else:
                    if signatures[filename] == design['signatures'][filename]:
                        del attachments[filename]

        for filename, value in attachments.iteritems():
            self.db.put_attachment(design, value, filename)
       
        # update signatures
        design = self.db[docid]
        design.update({'signatures': signatures})
        self.db[docid] = design