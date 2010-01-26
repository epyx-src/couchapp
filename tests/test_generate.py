#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.

import os
import tempfile
import sys
import unittest
import json

sys.path.insert(0, '..')

from couchapp.generator import generate_app
from couchapp.ui import UI
from couchapp.utils import deltree
from tests.utils import *

def _tempdir():
    f, fname = tempfile.mkstemp()
    os.unlink(fname)
    return fname


class GenerateTestCase(unittest.TestCase):    
    def setUp(self):
        self.ui = ui = UI()            
        self.appdir = _tempdir()
        os.makedirs(self.appdir)
        
    def tearDown(self):
        deltree(self.appdir)
        
    def testWritesAppNameInCouchapprc(self):
        generate_app(self.ui, os.path.join(self.appdir, 'blog'), None, True)
        conf = json.loads(readfile(os.path.join(self.appdir, 'blog', '.couchapprc')))
        self.assert_('blog', conf['env']['default']['name'])
        

if __name__ == '__main__':
    unittest.main()