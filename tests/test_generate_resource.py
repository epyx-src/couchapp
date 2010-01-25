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

from couchapp.resource_generator import ResourceGenerator
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
        ResourceGenerator(os.path.join('..', 'templates', 'resource')).generate(self.appdir, 'blog_post', {'attributes': 'title,author,body'})
        
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
        
    def testCreatesListOfAttributes(self):
        show_template = self.readfile('templates', 'blog_posts', 'show.mustache')
        self.assert_("{{#blog_post}}" in show_template)
        self.assert_('<input type="hidden" name="blog_post[_deleted]" value="true"/>' in show_template)
        self.assert_("<p class=\"title\">Title: {{title}}</p>" in show_template)
        self.assert_("<p class=\"author\">Author: {{author}}</p>" in show_template)
        self.assert_("<p class=\"body\">Body: {{body}}</p>" in show_template)
    
    def testGeneratesPluralLabel(self):
        index_template = self.readfile('templates', 'blog_posts', 'index.mustache')
        self.assert_("<h1>Blog Posts</h1>" in index_template)
        
    def testGeneratesSingularLabel(self):
        new_template = self.readfile('_attachments', 'blog_posts', 'new.html')
        self.assert_("<h1>New Blog Post</h1>" in new_template)
        
    def testGeneratesResourceNamesInLoops(self):
        new_template = self.readfile('_attachments', 'blog_posts', 'new.html')
        self.assert_('<label for="blog_post_title">Title</label>' in new_template)
        
    def testUseFirstAttributeForTests(self):
        test_template = self.readfile('test', 'blog_post_test.js')
        self.assert_("to_test(create_blog_post({title: 'test_title'})" in test_template)
        self.assert_("{xpath: \"//p[@class='title']\", validator: 'Title: test_title'}" in test_template)
    
    def testGeneratesCouchapprc(self):
        couchapprc_template = self.readfile('.couchapprc')
        self.assert_("http://localhost:5984/blog_post_test/" in couchapprc_template)
        
    def readfile(self, *in_app_path):
        in_app_path_string = os.path.join(*in_app_path)
        path = os.path.join(self.appdir, in_app_path_string)
        f = open(path, 'r')
        contents = f.read()
        f.close()
        return contents
    
if __name__ == '__main__':
    unittest.main()