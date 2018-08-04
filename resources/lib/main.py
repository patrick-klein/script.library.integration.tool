#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This module contains the class Main,
which gets called from the main executable and opens the main menu
'''

import os
import sys

import xbmc
import xbmcaddon
import xbmcgui

import resources.lib.utils as utils
from .blocked import Blocked
from .managed import ManagedMovies, ManagedTV
from .staged import StagedMovies, StagedTV
from .synced import Synced

# get tools depending on platform
if os.name == 'posix':
    import resources.lib.unix as fs
    utils.log_msg('Loaded unix module for system operations')
else:
    import resources.lib.universal as fs
    utils.log_msg('Loaded universal module for system operations')

# Define managed folder for use throughout code
MANAGED_FOLDER = xbmcaddon.Addon().getSetting('managed_folder')
utils.log_msg('managed_folder: %s' % MANAGED_FOLDER)


class Main(object):
    '''
    Perform basic initialization of folder structure
    and displays a window that leads to other menus.
    '''

    #TODO: unit tests
    #IDEA: use plugin menu system instead of dialog windows
    #TODO: option to automatically add movies & episodes with epids
    #TODO: option to automatically clean & update when adding/removing
    #TODO: add default location for managed folder
    #TODO: move database to special path
    #TODO: setting to delete all entries & managed folders, other than synced
    #TODO: new screenshots / tutorial / documentation
    #TODO: automatically check if item is already in library when staging? (or when adding)
    #TODO: option to call WatchedList if it's installed after updating library
    #IDEA: can you just add paths as sources?
    #TODO: support a centralized managed_folder that's shared over network
    #TODO: rebuild library option (flag currently managed items, move to staged,
    #      delete managed folder contents, then re-add flagged items)
    #TODO: multiple managed folders for split libraries
    #TODO: integrate WatchedList
    #TODO: move managed.db and ManagedTV/Movies to addon path, and only let metadata path
    #      be chosen

    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')

        # Create subfolders in managed_folder if they don't exist
        subfolders = [
            'ManagedMovies', 'ManagedTV', 'Metadata',
            os.path.join('Metadata', 'Movies'),
            os.path.join('Metadata', 'TV')
        ]
        created_folders = False
        for folder in subfolders:
            full_path = os.path.join(MANAGED_FOLDER, folder)
            if not os.path.isdir(full_path):
                fs.mkdir(full_path)
                created_folders = True
        if created_folders:
            STR_SUBFOLDERS_CREATED = self.addon.getLocalizedString(32127)
            utils.notification(STR_SUBFOLDERS_CREATED)
            sys.exit()

        # Open main menu
        self.view()

    def view(self):
        ''' displays main menu and leads to other modules '''
        #TODO: fix update library to only update path
        #TODO: remove extraneous tv show folders in Metadata
        #TODO: add parameter for location in list -
        #       useful when returning here after doing something on an item
        #       (preselect is broken when pressing cancel)
        STR_VIEW_MANAGED_MOVIES = self.addon.getLocalizedString(32002)
        STR_VIEW_MANAGED_TV_SHOWS = self.addon.getLocalizedString(32003)
        STR_VIEW_STAGED_MOVIES = self.addon.getLocalizedString(32004)
        STR_VIEW_STAGED_TV_SHOWS = self.addon.getLocalizedString(32005)
        STR_VIEW_SYNCED_DIRS = self.addon.getLocalizedString(32006)
        STR_VIEW_BLOCKED_ITEMS = self.addon.getLocalizedString(32007)
        STR_UPDATE_LIBRARY = xbmc.getLocalizedString(653).title()
        STR_CLEAN_LIBRARY = xbmc.getLocalizedString(14247).title()
        lines = [
            STR_VIEW_MANAGED_MOVIES, STR_VIEW_MANAGED_TV_SHOWS, STR_VIEW_STAGED_MOVIES,
            STR_VIEW_STAGED_TV_SHOWS, STR_VIEW_SYNCED_DIRS, STR_VIEW_BLOCKED_ITEMS,
            STR_UPDATE_LIBRARY, STR_CLEAN_LIBRARY
        ]
        ret = xbmcgui.Dialog().select(self.STR_ADDON_NAME, lines)
        if ret >= 0:

            if lines[ret] == STR_VIEW_MANAGED_MOVIES:
                ManagedMovies().view_all()

            elif lines[ret] == STR_VIEW_MANAGED_TV_SHOWS:
                ManagedTV().view_shows()

            elif lines[ret] == STR_VIEW_STAGED_MOVIES:
                StagedMovies().view_all()

            elif lines[ret] == STR_VIEW_STAGED_TV_SHOWS:
                StagedTV().view_shows()

            elif lines[ret] == STR_VIEW_SYNCED_DIRS:
                Synced().view()

            elif lines[ret] == STR_VIEW_BLOCKED_ITEMS:
                Blocked().view()

            elif lines[ret] == STR_UPDATE_LIBRARY:
                xbmc.executebuiltin('UpdateLibrary("video")')
                sys.exit()

            elif lines[ret] == STR_CLEAN_LIBRARY:
                xbmc.executebuiltin('CleanLibrary("video")')
                sys.exit()

            self.view()
