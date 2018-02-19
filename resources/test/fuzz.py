#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Defines function to call fuzz modules '''

import os
import sys
import unittest

import xbmc

from resources.lib.utils import log_msg
import resources.test.fuzz_utils

def Main():
    ''' get and call all fuzz modules '''

    # get test directory in addon folder
    test_path = xbmc.translatePath(
        'special://home/addons/script.library.integration.tool/resources/test/')

    # add all test modules to fuzz suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(sys.modules['resources.test.fuzz_utils']))
    log_msg('All fuzz tests: %s' % suite)

    # run all unit tests and save to text file
    log_file = os.path.join(test_path, 'fuzz_report.txt')
    with open(log_file, "w") as f:
        unittest.TextTestRunner(f, verbosity=2).run(suite)
