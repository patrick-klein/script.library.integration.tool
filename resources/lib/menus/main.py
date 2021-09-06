#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines the MainMenu class, which gets called from the main executable."""

import sys

import xbmc
import xbmcgui

from resources import ADDON_ID
from resources import ADDON_NAME

from resources.lib.misc import bold
from resources.lib.misc import color
from resources.lib.misc import getstring
from resources.lib.misc import videolibrary

from resources.lib.menus.managed_movies import ManagedMoviesMenu
from resources.lib.menus.staged_movies import StagedMoviesMenu
from resources.lib.menus.managed_tv import ManagedTVMenu
from resources.lib.menus.staged_tv import StagedTVMenu
# from resources.lib.menus.synced import SyncedMenu
from resources.lib.menus.blocked import BlockedMenu

# from resources.lib.dialog_select import Select

# TODO: automatically clean & update when adding/removing based in type and path
# TODO: support a centralized managed_folder that's shared over network
# TODO: rebuild library option
#   1. FLAG all itens in managed
#   2. move all all to staged
#   3. delete all managed itens
#   4. re-add all FLAGGED itens
# TODO: integrate WatchedList
# TODO: option to call WatchedList if it's installed after updating library
# IDEA: use plugin menu system instead of dialog windows
# TODO: Put all classes in their own file, change menu classes to ManagedMenu, StagedMenu, etc.


class MainMenu(object):
    """
    Perform basic initialization of folder structure.

    Display displays a window that leads to other menus.
    """

    def __init__(self, database, progressbar):
        """__init__ MainMenu."""
        self.database = database
        self.progressbar = progressbar
        self.lastchoice = False

    def library_options(self):
        """Display dedicated menu to Library functions."""
        OPTIONS = {
            653: 'scan',
            14247: 'clean',
        }
        selection = xbmcgui.Dialog().select(
            heading='%s - %s' % (ADDON_NAME, color(bold('Library options'))),
            list=[xbmc.getLocalizedString(x).title() for x in OPTIONS],
            useDetails=True,
            preselect=self.lastchoice
        )
        self.lastchoice = selection
        if selection >= 0:
            arg = OPTIONS[list(OPTIONS.keys())[selection]]
            if arg:
                videolibrary(arg)
                # sleep to wait library update, whithout this
                xbmc.sleep(2500)
            self.view()
        else:
            self.view()
        sys.exit()

    def view(self):
        """Display main menu which leads to other menus."""
        OPTIONS = {
            32002: ManagedMoviesMenu(self.database, self.progressbar).view_all,
            32004: StagedMoviesMenu(self.database, self.progressbar).view_all,
            32003: ManagedTVMenu(self.database, self.progressbar).view_shows,
            32005: StagedTVMenu(self.database, self.progressbar).view_shows,
            # 32006: SyncedMenu(self.database, self.progressbar).view,
            32007: BlockedMenu(self.database, self.progressbar).view,
            32180: self.library_options,
            32179: xbmc.executebuiltin,
        }
        selection = xbmcgui.Dialog().select(
            heading=bold(ADDON_NAME),
            list=[getstring(x) for x in OPTIONS],
            useDetails=True,
            preselect=self.lastchoice
        )
        self.lastchoice = selection
        if selection >= 0:
            command = OPTIONS[list(OPTIONS.keys())[selection]]
            if command:
                if xbmc.executebuiltin == command:
                    command('Addon.OpenSettings(%s)' % ADDON_ID)
                    return
                command()
            self.view()
        sys.exit()
