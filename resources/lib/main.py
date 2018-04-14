#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This module contains the class Main,
which gets called from the main executable and opens the main menu
'''

import os
import sys
import xbmc
import xbmcgui
import xbmcaddon

from managed import ManagedMovies, ManagedTV
from staged import StagedMovies, StagedTV
from synced import Synced
from blocked import Blocked
from utils import log_msg, notification
import update_pkl

# get tools depending on platform
if os.name == 'posix':
    import unix as fs
    log_msg('Loaded unix module for system operations')
else:
    import universal as fs
    log_msg('Loaded universal module for system operations')

# define managed folder for use throughout code
MANAGED_FOLDER = xbmcaddon.Addon().getSetting('managed_folder')
log_msg('managed_folder: %s' % MANAGED_FOLDER)

class Main(object):
    '''
    performs basic initialization of folder structure
    and displays a window that leads to other class options
    '''
    #TODO: unit tests
    #TODO: mark strm items as watched after played
    #TODO?: use plugin menu system instead of dialog windows
    #TODO: option to automatically add movies & episodes with epids
    #TODO: option to automatically clean & update when adding/removing
    #TODO: add default location for managed folder
    #TODO: move database to special path

    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')

        # Display an error is user hasn't configured managed folder yet
        if not (MANAGED_FOLDER and os.path.isdir(MANAGED_FOLDER)):
            #TODO: open prompt to just set managed folder from here
            STR_CHOOSE_FOLDER = self.addon.getLocalizedString(32123)
            notification(STR_CHOOSE_FOLDER)
            log_msg('No managed folder!', xbmc.LOGERROR)
            sys.exit()

        if any(['.pkl' in x for x in os.listdir(MANAGED_FOLDER)]):
            update_pkl.main()

        # Create subfolders in managed_folder if they don't exist
        subfolders = ['ManagedMovies', 'ManagedTV', 'Metadata',
                      os.path.join('Metadata', 'Movies'),
                      os.path.join('Metadata', 'TV')]
        created_folders = False
        for folder in subfolders:
            full_path = os.path.join(MANAGED_FOLDER, folder)
            if not os.path.isdir(full_path):
                fs.mkdir(full_path)
                created_folders = True
        if created_folders:
            STR_SUBFOLDERS_CREATED = self.addon.getLocalizedString(32127)
            notification(STR_SUBFOLDERS_CREATED)
            sys.exit()

        # Open main menu
        self.view()

    def view(self):
        ''' displays main menu and leads to other modules '''
        #TODO: fix update library to only update path
        #TODO: remove extraneous tv show folders in Metadata
        #TODO: rebuild managed list (remove all items, then re-add new instance of ContentItem)
        #TODO: add parameter for location in list -
        #       useful when returning here after doing something on an item
        #       (preselct is broken when pressing cancel)
        STR_VIEW_MANAGED_MOVIES = self.addon.getLocalizedString(32002)
        STR_VIEW_MANAGED_TV_SHOWS = self.addon.getLocalizedString(32003)
        STR_VIEW_STAGED_MOVIES = self.addon.getLocalizedString(32004)
        STR_VIEW_STAGED_TV_SHOWS = self.addon.getLocalizedString(32005)
        STR_VIEW_SYNCED_DIRS = self.addon.getLocalizedString(32006)
        STR_VIEW_BLOCKED_ITEMS = self.addon.getLocalizedString(32007)
        STR_UPDATE_LIBRARY = xbmc.getLocalizedString(653).title()
        STR_CLEAN_LIBRARY = xbmc.getLocalizedString(14247).title()
        lines = [STR_VIEW_MANAGED_MOVIES, STR_VIEW_MANAGED_TV_SHOWS,
                 STR_VIEW_STAGED_MOVIES, STR_VIEW_STAGED_TV_SHOWS,
                 STR_VIEW_SYNCED_DIRS, STR_VIEW_BLOCKED_ITEMS,
                 STR_UPDATE_LIBRARY, STR_CLEAN_LIBRARY]
        ret = xbmcgui.Dialog().select(self.STR_ADDON_NAME, lines)
        if not ret < 0:

            if lines[ret] == STR_VIEW_MANAGED_MOVIES:
                menu = ManagedMovies(self)
                menu.view_all()

            elif lines[ret] == STR_VIEW_MANAGED_TV_SHOWS:
                menu = ManagedTV(self)
                menu.view_shows()

            elif lines[ret] == STR_VIEW_STAGED_MOVIES:
                menu = StagedMovies(self)
                menu.view_all()

            elif lines[ret] == STR_VIEW_STAGED_TV_SHOWS:
                menu = StagedTV(self)
                menu.view_shows()

            elif lines[ret] == STR_VIEW_SYNCED_DIRS:
                menu = Synced(self)
                menu.view()

            elif lines[ret] == STR_VIEW_BLOCKED_ITEMS:
                menu = Blocked(self)
                menu.view()

            elif lines[ret] == STR_UPDATE_LIBRARY:
                xbmc.executebuiltin('UpdateLibrary("video")')

            elif lines[ret] == STR_CLEAN_LIBRARY:
                xbmc.executebuiltin('CleanLibrary("video")')
