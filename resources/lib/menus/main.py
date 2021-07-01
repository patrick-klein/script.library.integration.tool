#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines the MainMenu class, which gets called from the main executable."""
import sys

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

from resources import ADDON_NAME

from resources.lib.utils import colored_str
from resources.lib.utils import videolibrary
from resources.lib.utils import getlocalizedstring


class MainMenu(object):
    """
    Perform basic initialization of folder structure.

    Display displays a window that leads to other menus.
    """

    def __init__(self, database):
        """__init__ MainMenu."""
        self.database = database
    # IDEA: use plugin menu system instead of dialog windows
    # TODO: option to automatically add movies & episodes with epids
    # TODO: option to automatically clean & update when adding/removing
    # TODO: new screenshots / tutorial / documentation
    # TODO: automatically check if item is already in library when staging? (or when adding)
    # TODO: option to call WatchedList if it's installed after updating library
    # TODO: support a centralized managed_folder that's shared over network
    # TODO: rebuild library option (flag currently managed items, move to staged,
    #      delete managed folder contents, then re-add flagged items)
    # TODO: multiple managed folders for split libraries
    # TODO: integrate WatchedList
    # TODO: Put all classes in their own file, change menu classes to ManagedMenu, StagedMenu, etc.

    def view(self):
        """Display main menu which leads to other menus."""
        # TODO: fix update library to only update path
        # TODO: remove extraneous tv show folders in Metadata
        # TODO: add parameter for location in list -
        #       useful when returning here after doing something on an item
        #       (preselect is broken when pressing cancel)

        STR_VIEW_MANAGED_MOVIES = colored_str(
            getlocalizedstring(32002), 'darkslateblue')
        STR_VIEW_MANAGED_TV_SHOWS = colored_str(
            getlocalizedstring(32003), 'darkslateblue')
        STR_VIEW_STAGED_MOVIES = colored_str(
            getlocalizedstring(32004), 'darkolivegreen')
        STR_VIEW_STAGED_TV_SHOWS = colored_str(
            getlocalizedstring(32005), 'darkolivegreen')
        STR_VIEW_SYNCED_DIRS = getlocalizedstring(32006)
        STR_VIEW_BLOCKED_ITEMS = getlocalizedstring(32007)
        STR_UPDATE_LIBRARY = xbmc.getLocalizedString(653).title()
        STR_CLEAN_LIBRARY = xbmc.getLocalizedString(14247).title()
        lines = [
            STR_VIEW_MANAGED_MOVIES,
            STR_VIEW_STAGED_MOVIES,
            STR_VIEW_MANAGED_TV_SHOWS,
            STR_VIEW_STAGED_TV_SHOWS,
            STR_VIEW_SYNCED_DIRS,
            STR_VIEW_BLOCKED_ITEMS,
            STR_UPDATE_LIBRARY,
            STR_CLEAN_LIBRARY
        ]
        ret = xbmcgui.Dialog().select(
            '[B]%s[/B]' % ADDON_NAME,
            lines
        )
        if ret >= 0:
            if lines[ret] == STR_VIEW_MANAGED_MOVIES:
                from resources.lib.menus.managed_movies import ManagedMoviesMenu
                ManagedMoviesMenu(database=self.database).view_all()
            elif lines[ret] == STR_VIEW_STAGED_MOVIES:
                from resources.lib.menus.staged_movies import StagedMoviesMenu
                StagedMoviesMenu(database=self.database).view_all()
            elif lines[ret] == STR_VIEW_MANAGED_TV_SHOWS:
                from resources.lib.menus.managed_tv import ManagedTVMenu
                ManagedTVMenu(database=self.database).view_shows()
            elif lines[ret] == STR_VIEW_STAGED_TV_SHOWS:
                from resources.lib.menus.staged_tv import StagedTVMenu
                StagedTVMenu(database=self.database).view_shows()
            elif lines[ret] == STR_VIEW_SYNCED_DIRS:
                from resources.lib.menus.synced import SyncedMenu
                SyncedMenu(database=self.database).view()
            elif lines[ret] == STR_VIEW_BLOCKED_ITEMS:
                from resources.lib.menus.blocked import BlockedMenu
                BlockedMenu(database=self.database).view()
            elif lines[ret] == STR_UPDATE_LIBRARY:
                videolibrary('scan')
                sys.exit()
            elif lines[ret] == STR_CLEAN_LIBRARY:
                videolibrary('clean')
                sys.exit()
            self.view()
