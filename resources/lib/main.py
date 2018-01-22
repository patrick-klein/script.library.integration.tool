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
from utils import log_msg

# define managed folder for use throughout code
MANAGED_FOLDER = xbmcaddon.Addon().getSetting('managed_folder')
log_msg('managed_folder: %s' % MANAGED_FOLDER)

class Main(object):
    '''
    performs basic initialization of folder structure
    and displays a window that leads to other class options
    '''
    #TODO: use sqlite database... will lead to LOTS of optimizations
    #TODO: unit tests
    #TODO: mark strm items as watched after played
    #?TODO: use plugin menu system instead of dialog windows
    #TODO: option to automatically add movies & episodes with epids
    #TODO: option to automatically clean & update when adding/removing
    #TODO: add default location for managed folder
    #TODO: move pickle files to special path

    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')

        # Display an error is user hasn't configured managed folder yet
        if not MANAGED_FOLDER:
            STR_CHOOSE_FOLDER = self.addon.getLocalizedString(32123)
            xbmc.executebuiltin(
                'Notification("{0}", "{1}")'.format(
                    self.STR_ADDON_NAME, STR_CHOOSE_FOLDER))
            log_msg('No managed folder!', xbmc.LOGERROR)
            sys.exit()

        # Create subfolders in managed_folder if they don't exist
        created_folders = False
        if not os.path.isdir(os.path.join(MANAGED_FOLDER, 'ManagedMovies')):
            os.system('mkdir "%s"' % os.path.join(MANAGED_FOLDER, 'ManagedMovies'))
            created_folders = True
        if not os.path.isdir(os.path.join(MANAGED_FOLDER, 'ManagedTV')):
            os.system('mkdir "%s"' % os.path.join(MANAGED_FOLDER, 'ManagedTV'))
            created_folders = True
        if not os.path.isdir(os.path.join(MANAGED_FOLDER, 'Metadata')):
            os.system('mkdir "%s"' % os.path.join(MANAGED_FOLDER, 'Metadata'))
            created_folders = True
        if not os.path.isdir(os.path.join(MANAGED_FOLDER, 'Metadata', 'Movies')):
            os.system('mkdir "%s"' % os.path.join(MANAGED_FOLDER, 'Metadata', 'Movies'))
            created_folders = True
        if not os.path.isdir(os.path.join(MANAGED_FOLDER, 'Metadata', 'TV')):
            os.system('mkdir "%s"' % os.path.join(MANAGED_FOLDER, 'Metadata', 'TV'))
            created_folders = True
        if created_folders:
            STR_SUBFOLDERS_CREATED = self.addon.getLocalizedString(32127)
            xbmc.executebuiltin(
                'Notification("{0}", "{1}")'.format(
                    self.STR_ADDON_NAME, STR_SUBFOLDERS_CREATED))
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
