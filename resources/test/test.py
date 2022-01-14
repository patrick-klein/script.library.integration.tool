#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines function to call test modules and find coverage."""


import os
import sys
import unittest

import xbmc
import xbmcvfs

from resources.lib.log import log_msg
from resources.lib.misc import notification


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
    log_msg(f"All unit tests: {suite}")

    # Attempt to load and start coverage module
    try:
        sys.path.append(
            '/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages'
        )
        import coverage
    except ImportError:
        test_coverage = False
        log_msg('Coverage module not available.', xbmc.LOGWARNING)
    else:
        test_path_wildcard = os.path.join(test_path, '*')
        cov = coverage.Coverage(omit=test_path_wildcard)
        cov.start()
        test_coverage = True
        log_msg('Coverage module loaded.')

    # Run all unit tests and save to text file
    log_file = os.path.join(test_path, 'test_report.txt')
    with open(log_file, 'w', encoding="utf-8") as log_file_write:
        result = unittest.TextTestRunner(
            log_file_write,
            verbosity=2
        ).run(suite)

    # Stop coverage and save output
    if test_coverage:
        cov.stop()
        cov_folder = os.path.join(test_path, 'coverage')
        cov.html_report(directory=cov_folder)
        cov_txt_file = os.path.join(test_path, 'coverage.txt')
        with open(cov_txt_file, 'w', encoding="utf-8") as cov_txt_file_write:
            cov.report(
                file=cov_txt_file_write
            )
        cov_xml_file = os.path.join(test_path, 'coverage.xml')
        cov.xml_report(outfile=cov_xml_file)
        log_msg('Test coverage complete.')

    if result.wasSuccessful():
        notification('Tests successful')
    else:
        notification('Tests failed')

    log_msg(f"Test result: {result}")
