#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines function to call test modules and find coverage."""


import os
import sys
import unittest

import xbmc
import xbmcvfs

import resources.lib.utils as utils


def test():
    """Get and call all test modules and find coverage."""
    # Get test directory in addon folder
    test_path = xbmcvfs.translatePath(
        'special://home/addons/script.library.integration.tool/resources/test/'
    )

    # Add all test modules to suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.discover(
        os.path.dirname(__file__), pattern='test_*.py'))
    utils.log_msg('All unit tests: %s' % suite)

    # Attempt to load and start coverage module
    try:
        sys.path.append(
            '/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages'
        )
        import coverage
    except ImportError:
        test_coverage = False
        utils.log_msg('Coverage module not available.', xbmc.LOGWARNING)
    else:
        test_path_wildcard = os.path.join(test_path, '*')
        cov = coverage.Coverage(omit=test_path_wildcard)
        cov.start()
        test_coverage = True
        utils.log_msg('Coverage module loaded.')

    # Run all unit tests and save to text file
    log_file = os.path.join(test_path, 'test_report.txt')
    with open(log_file, 'w') as f:
        result = unittest.TextTestRunner(f, verbosity=2).run(suite)

    # Stop coverage and save output
    if test_coverage:
        cov.stop()
        cov_folder = os.path.join(test_path, 'coverage')
        cov.html_report(directory=cov_folder)
        cov_txt_file = os.path.join(test_path, 'coverage.txt')
        with open(cov_txt_file, 'w') as f:
            cov.report(file=f)
        cov_xml_file = os.path.join(test_path, 'coverage.xml')
        cov.xml_report(outfile=cov_xml_file)
        utils.log_msg('Test coverage complete.')

    if result.wasSuccessful():
        utils.notification('Tests successful')
    else:
        utils.notification('Tests failed')

    utils.log_msg('Test result: %s' % result)
