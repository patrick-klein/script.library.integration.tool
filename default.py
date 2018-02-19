#!/usr/bin/python
# -*- coding: utf-8 -*-
''' main entry point for addon '''

import sys

if __name__ == '__main__':

    if len(sys.argv) == 1:
        import resources.lib.main as main
        main.Main()

    elif sys.argv[1] == 'test':
        import resources.test.test as test
        test.Main()

    elif sys.argv[1] == 'fuzz':
        import resources.test.fuzz as fuzz
        fuzz.Main()
