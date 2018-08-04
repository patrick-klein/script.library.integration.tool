#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Defines function to call test modules and find coverage '''

import os
import sys
import unittest

import xbmc

from resources.lib.utils import log_msg
import resources.test.test_utils


def Test():
    ''' get and call all test modules and find coverage '''

    # get test directory in addon folder
    test_path = xbmc.translatePath(
        'special://home/addons/script.library.integration.tool/resources/test/'
    )

    # add all test modules to suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    # TODO: Add tests using discover
    suite.addTests(loader.loadTestsFromModule(sys.modules['resources.test.test_utils']))
    log_msg('All unit tests: %s' % suite)

    # attempt to load and start coverage module
    try:
        sys.path.append(
            '/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages'
        )
        import coverage
        test_path_wildcard = os.path.join(test_path, '*')
        cov = coverage.Coverage(omit=test_path_wildcard)
        cov.start()
        test_coverage = True
        log_msg('Coverage module loaded.')
    except ImportError:
        test_coverage = False
        log_msg('Coverage module not available.', xbmc.LOGWARNING)

    # run all unit tests and save to text file
    log_file = os.path.join(test_path, 'test_report.txt')
    with open(log_file, 'w') as f:
        unittest.TextTestRunner(f, verbosity=2).run(suite)

    # stop coverage and save output
    if test_coverage:
        cov.stop()
        cov_folder = os.path.join(test_path, 'coverage')
        cov.html_report(directory=cov_folder)
        cov_txt_file = os.path.join(test_path, 'coverage.txt')
        with open(cov_txt_file, 'w') as f:
            cov.report(file=f)
        cov_xml_file = os.path.join(test_path, 'coverage.xml')
        cov.xml_report(outfile=cov_xml_file)
        log_msg('Test coverage complete.')
