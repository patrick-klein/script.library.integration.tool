#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the MainMenu class,
which gets called from the main executable
'''
import sys

import xbmc
import xbmcgui

import resources.lib.utils as utils

class MainMenu(object):
    ''' Perform basic initialization of folder structure
    and displays a window that leads to other menus '''

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
        ''' Displays main menu which leads to other menus '''
        # TODO: fix update library to only update path
        # TODO: remove extraneous tv show folders in Metadata
        # TODO: add parameter for location in list -
        #       useful when returning here after doing something on an item
        #       (preselect is broken when pressing cancel)
        STR_VIEW_MANAGED_MOVIES = utils.getLocalizedString(32002)
        STR_VIEW_MANAGED_TV_SHOWS = utils.getLocalizedString(32003)
        STR_VIEW_STAGED_MOVIES = utils.getLocalizedString(32004)
        STR_VIEW_STAGED_TV_SHOWS = utils.getLocalizedString(32005)
        STR_VIEW_SYNCED_DIRS = utils.getLocalizedString(32006)
        STR_VIEW_BLOCKED_ITEMS = utils.getLocalizedString(32007)
        STR_UPDATE_LIBRARY = xbmc.getLocalizedString(653).title()
        STR_CLEAN_LIBRARY = xbmc.getLocalizedString(14247).title()
        lines = [
            STR_VIEW_MANAGED_MOVIES, STR_VIEW_MANAGED_TV_SHOWS, STR_VIEW_STAGED_MOVIES,
            STR_VIEW_STAGED_TV_SHOWS, STR_VIEW_SYNCED_DIRS, STR_VIEW_BLOCKED_ITEMS,
            STR_UPDATE_LIBRARY, STR_CLEAN_LIBRARY
        ]
        ret = xbmcgui.Dialog().select(utils.ADDON_NAME, lines)
        if ret >= 0:

            if lines[ret] == STR_VIEW_MANAGED_MOVIES:
                from .managed_movies import ManagedMoviesMenu
                ManagedMoviesMenu().view_all()

            elif lines[ret] == STR_VIEW_MANAGED_TV_SHOWS:
                from .managed_tv import ManagedTVMenu
                ManagedTVMenu().view_shows()

            elif lines[ret] == STR_VIEW_STAGED_MOVIES:
                from .staged_movies import StagedMoviesMenu
                StagedMoviesMenu().view_all()

            elif lines[ret] == STR_VIEW_STAGED_TV_SHOWS:
                from .staged_tv import StagedTVMenu
                StagedTVMenu().view_shows()

            elif lines[ret] == STR_VIEW_SYNCED_DIRS:
                from .synced import SyncedMenu
                SyncedMenu().view()

            elif lines[ret] == STR_VIEW_BLOCKED_ITEMS:
                from .blocked import BlockedMenu
                BlockedMenu().view()

            elif lines[ret] == STR_UPDATE_LIBRARY:
                utils.videolibrary('scan')
                sys.exit()

            elif lines[ret] == STR_CLEAN_LIBRARY:
                utils.videolibrary('clean')
                sys.exit()

            self.view()
