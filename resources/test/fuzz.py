#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines function to call fuzz modules
'''

import os
import unittest

import xbmc # pylint: disable=import-error

import resources.lib.utils as utils


def fuzz():
    ''' Get and call all fuzz modules '''

    # Get test directory in addon folder
    test_path = xbmc.translatePath(
        'special://home/addons/script.library.integration.tool/resources/test/'
    )

    # Add all test modules to fuzz suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.discover(os.path.dirname(__file__), pattern='fuzz_*.py'))
    utils.log_msg('All fuzz tests: %s' % suite)

    # Run all unit tests and save to text file
    log_file = os.path.join(test_path, 'fuzz_report.txt')
    with open(log_file, "w") as f:
        result = unittest.TextTestRunner(f, verbosity=2).run(suite)

    if result.wasSuccessful():
        utils.notification('Fuzz successful')
    else:
        utils.notification('Fuzz failed')

    utils.log_msg('Fuzz result: %s' % result)
