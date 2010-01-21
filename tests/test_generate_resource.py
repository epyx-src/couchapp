#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.

import os
import tempfile
import shutil
import sys
import unittest

sys.path.insert(0,'..')

from couchapp.app import generate
from couchapp.ui import UI
from couchapp.utils import deltree


def _tempdir():
    f, fname = tempfile.mkstemp()
    os.unlink(fname)
    return fname


class GenerateResourceTestCase(unittest.TestCase):
    
    def setUp(self):
        self.ui = ui = UI()            
        self.appdir = _tempdir()
        os.makedirs(self.appdir)
        generate(self.ui, self.appdir, 'resource', 'blog_post', **{'attributes': 'title,author,body'})
        
    def tearDown(self):
        deltree(self.appdir)

    def testGeneratesFilesWithPluralNames(self):
        list_file = self.readfile('lists', 'blog_posts.js')
        self.assert_("// !json templates.blog_posts.index" in list_file)
        self.assert_("CouchApp.path.showPath('blog_post', this._id);" in list_file)
        
    def testGeneratesFilesWithSingularNames(self):
        show_file = self.readfile('shows', 'edit_blog_post.js')
        self.assert_("// !json templates.blog_posts.edit" in show_file)
        self.assert_("blog_post: [doc]," in show_file)
        self.assert_("CouchApp.path.showPath('blog_post', doc['_id'])" in show_file)
        self.assert_("CouchApp.path.updatePath('blog_post', doc['_id'])" in show_file)
    
    def testGeneratesDirectoriesWithPluralNames(self):
        self.assert_(os.path.isdir(os.path.join(self.appdir, 'views', 'blog_posts')) == True)
    
    def readfile(self, *in_app_path):
        in_app_path_string = os.path.join(*in_app_path)
        path = os.path.join(self.appdir, in_app_path_string)
        f = open(path, 'r')
        contents = f.read()
        f.close()
        return contents
    
if __name__ == '__main__':
    unittest.main()