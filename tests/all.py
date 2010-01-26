import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from test_generate_resource import *
from test_cli import CliTestCase
from test_couchdbclient import *
from test_generate import *

if __name__ == '__main__':
    unittest.main()