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
import StringIO
import json

sys.path.insert(0, '..')

from couchapp.resource_generator import *
from couchapp.ui import UI
from couchapp.utils import deltree
from tests.utils import *

def _tempdir():
    f, fname = tempfile.mkstemp()
    os.unlink(fname)
    return fname


class GenerateResourceTestCase(unittest.TestCase):
    
    def setUp(self):
        self.ui = ui = UI()            
        self.appdir = _tempdir()
        os.makedirs(self.appdir)
        path = os.path.normpath(os.path.join(os.getcwd(), 
                                '..', 'templates', 'resource'))
        self.generator = ResourceGenerator(path, ui)
        self.generator.cli.outIO = StringIO.StringIO()
        self.startdir = os.getcwd()
        
    def tearDown(self):
        deltree(self.appdir)
        os.chdir(self.startdir)
        
    def testFailsIfNotAttributesGiven(self):
        self.generator.generate(self.appdir, 
                            'blog_post', {'attributes': ''})
        self.assert_(os.path.isdir(os.path.join(self.appdir, 
                'views', 'blog_posts')) == False)
        self.assert_(self.generator.cli.outIO.getvalue() == 'No attributes given. Please add --attributes att1,att2...\n')
    
    def testGeneratesFilesWithPluralNames(self):
        self.run_generate()
        list_file = readfile(self.appdir, 'lists', 'blog_posts.js')
        self.assert_("// !json templates.blog_posts.index" in list_file)
        self.assert_("CouchApp.path.showPath('blog_post', this._id);" in list_file)
        
    def testGeneratesFilesWithSingularNames(self):
        self.run_generate()
        show_file = readfile(self.appdir, 'shows', 'edit_blog_post.js')
        self.assert_("// !json templates.blog_posts.edit" in show_file)
        self.assert_("blog_post: [doc]," in show_file)
        self.assert_("CouchApp.path.showPath('blog_post', doc['_id'])" in show_file)
        self.assert_("CouchApp.path.updatePath('blog_post', doc['_id'])" in show_file)
    
    def testGeneratesDirectoriesWithPluralNames(self):
        self.run_generate()
        self.assert_(os.path.isdir(os.path.join(self.appdir, 'views', 'blog_posts')) == True)
        
    def testCreatesListOfAttributes(self):
        self.run_generate()
        show_template = readfile(self.appdir, 'templates', 
                            'blog_posts', 'show.mustache')
        self.assert_("{{#blog_post}}" in show_template)
        self.assert_('<input type="hidden" name="blog_post[_deleted]" value="true"/>' in show_template)
        self.assert_("<p class=\"title\">Title: {{title}}</p>" in show_template)
        self.assert_("<p class=\"author\">Author: {{author}}</p>" in show_template)
        self.assert_("<p class=\"body\">Body: {{body}}</p>" in show_template)
    
    def testGeneratesPluralLabel(self):
        self.run_generate()
        index_template = readfile(self.appdir, 'templates', 'blog_posts', 'index.mustache')
        self.assert_("<h1>Blog Posts</h1>" in index_template)
        
    def testGeneratesSingularLabel(self):
        self.run_generate()
        new_template = readfile(self.appdir, '_attachments', 'blog_posts', 'new.html')
        self.assert_("<h1>New Blog Post</h1>" in new_template)
        
    def testGeneratesResourceNamesInLoops(self):
        self.run_generate()
        new_template = readfile(self.appdir, '_attachments', 'blog_posts', 'new.html')
        self.assert_('<label for="blog_post_title">Title</label>' in new_template)
        
    def testUsesFirstAttributeForTests(self):
        self.run_generate()
        test_template = readfile(self.appdir, 'test', 'blog_post_test.js')
        self.assert_("to_test(create_blog_post({title: 'test_title'})" in test_template)
        self.assert_("{xpath: \"//p[@class='title']\", validator: 'Title: test_title'}" in test_template)
    
    def testGeneratesAppUrl(self):
        self.generator.cli = self.FakeCli(True)
        writefile('{"env": {"default": {"name": "blog"}}}', self.appdir, '.couchapprc')
        self.generator.ui.updateconfig(self.appdir)
        self.run_generate()
        test_template = readfile(self.appdir, 'test', 'blog_post_test.js')
        self.assert_("var app_url = 'http://localhost:5984/blog_test/_design/blog/'" in test_template)
    
    def testGeneratesCouchapprc(self):
        self.generator.cli = self.FakeCli(True)
        writefile('{"env": {"default": {"name": "blog"}}}', self.appdir, '.couchapprc')
        self.generator.ui.updateconfig(self.appdir)
        self.run_generate()
        couchapprc_template = readfile(self.appdir, '.couchapprc')
        self.assert_("http://localhost:5984/blog_test/" in couchapprc_template)
    
    def testExtendsCouchapprc(self):
        self.generator.cli = self.FakeCli(True)
        writefile('{"env": {"default": {"name": "blog"}}}', self.appdir, '.couchapprc')
        self.generator.ui.updateconfig(self.appdir)
        self.run_generate()
        couchapprc = json.loads(readfile(self.appdir, '.couchapprc'))
        self.assert_("blog" in couchapprc['env']['default']['name'])
    
    def testDoesNotExtendCouchapprcIfDbIsAlreadyThere(self):
        self.generator.cli = self.FakeCli(True)
        writefile('{"env": {"test": {"db": "my_db"}}}', self.appdir, '.couchapprc')
        self.generator.ui.updateconfig(self.appdir)
        self.run_generate()
        couchapprc = json.loads(readfile(self.appdir, '.couchapprc'))
        self.assert_("my_db" in couchapprc['env']['test']['db'])
        
    def testAsksBeforeOverwritingFiles(self):
        cli = self.FakeCli(True)
        self.generator.cli = cli
        os.makedirs(os.path.join(self.appdir, 'vendor'))
        writefile('my fake content', self.appdir, 'vendor', 'mustache.js')
        self.run_generate()
        self.assert_(cli.asked() == 'really overwrite vendor/mustache.js?')
    
    def testDoesNotOverwriteIfAnswerIsNo(self):
        cli = self.FakeCli(False)
        self.generator.cli = cli
        os.makedirs(os.path.join(self.appdir, 'vendor'))
        writefile('my fake content', self.appdir, 'vendor', 'mustache.js')
        self.run_generate()
        self.assert_('my fake content' in readfile(self.appdir, 'vendor', 'mustache.js'))
        
    def testOverwritesIfAnswerIsYes(self):
        cli = self.FakeCli(True)
        self.generator.cli = cli
        os.makedirs(os.path.join(self.appdir, 'vendor'))
        writefile('my fake content', self.appdir, 'vendor', 'mustache.js')
        self.run_generate()
        self.assert_('my fake content' != readfile(self.appdir, 'vendor', 'mustache.js'))
                
    def run_generate(self):
        self.generator.generate(self.appdir, 
                'blog_post', {'attributes': 'title,author,body'})
    
    class FakeCli(object):
        def __init__(self, ask_return_value):
            self.ask_return_value = ask_return_value
            self._asked = ""

        def ask(self, question):
            self._asked = question
            return self.ask_return_value

        def asked(self):
            return self._asked

        def tell(self, statement):
            pass
    

class CliTestCase(unittest.TestCase):
    class FakeInput(object):
        i = -1
        
        def __init__(self, *_input):
            self.input = _input
        
        def readline(self):
            self.i += 1
            return self.input[self.i]
            
    def testTellPrintsOutStatement(self):
        _out = StringIO.StringIO()
        cli = Cli(None, _out)
        cli.tell("done")
        self.assert_(_out.getvalue() == "done\n")
            
    def testPrintsTheQuestion(self):
        _in = StringIO.StringIO("y\n")
        _out = StringIO.StringIO()
        cli = Cli(_in, _out)
        cli.ask('something')
        self.assert_(_out.getvalue() == "something [y/n]: ")
    
    def testWhenAnsweringWithYReturnsTrue(self):
        _in = StringIO.StringIO("y\n")
        cli = Cli(_in, StringIO.StringIO())
        self.assert_(cli.ask('something') == True)
    
    def testWhenAnsweringWithNReturnsFalse(self):
        _in = StringIO.StringIO("n\n")
        cli = Cli(_in, StringIO.StringIO())
        self.assert_(cli.ask('something') == False)
        
    def testAsksAgainOnInvalidInput(self):
        _in = self.FakeInput("x\n", "y\n")
        _out = StringIO.StringIO()
        cli = Cli(_in, _out)
        cli.ask('something')
        self.assert_(_out.getvalue() == "something [y/n]: something [y/n]: ")
        
if __name__ == '__main__':
    unittest.main()