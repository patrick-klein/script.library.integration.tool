#!/usr/bin/python
# -*- coding: utf-8 -*-
'''This modules gets called by the main executable'''

import sys
import resources.lib.utils as utils


@utils.entrypoint
def main():
    '''Main entry point for addon'''

    if len(sys.argv) == 1:
        from resources.lib.menus.main import MainMenu
        MainMenu().view()

    elif sys.argv[1] == 'test':
        from resources.test.test import test
        test()

    elif sys.argv[1] == 'fuzz':
        from resources.test.fuzz import fuzz
        fuzz()


if __name__ == '__main__':
    main()
