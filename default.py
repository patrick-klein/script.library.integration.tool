#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Main entry point for addon '''

import sys

import resources.lib.utils as utils


@utils.entrypoint
def main():
    ''' Main entry point for addon '''

    if len(sys.argv) == 1:
        from resources.lib.main import Main
        Main()

    elif sys.argv[1] == 'test':
        from resources.test.test import Test
        Test()

    elif sys.argv[1] == 'fuzz':
        from resources.test.fuzz import Fuzz
        Fuzz()


if __name__ == '__main__':
    main()
