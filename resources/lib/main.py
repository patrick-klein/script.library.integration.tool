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
    #!TODO: documentation

    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')

        # Display an error is user hasn't configured managed folder yet
        if not MANAGED_FOLDER:
            str_choose_folder = self.addon.getLocalizedString(32123)
            xbmc.executebuiltin(
                'Notification("{0}", "{1}")'.format(
                    self.STR_ADDON_NAME, str_choose_folder))
            log_msg('No managed folder!', xbmc.LOGERROR)
            sys.exit()

        # Create subfolders in managed_folder if they don't exist
        if not os.path.isdir(os.path.join(MANAGED_FOLDER, 'ManagedMovies')):
            os.system('mkdir "%s"' % os.path.join(MANAGED_FOLDER, 'ManagedMovies'))
        if not os.path.isdir(os.path.join(MANAGED_FOLDER, 'ManagedTV')):
            os.system('mkdir "%s"' % os.path.join(MANAGED_FOLDER, 'ManagedTV'))
        if not os.path.isdir(os.path.join(MANAGED_FOLDER, 'Metadata')):
            os.system('mkdir "%s"' % os.path.join(MANAGED_FOLDER, 'Metadata'))
        if not os.path.isdir(os.path.join(MANAGED_FOLDER, 'Metadata', 'Movies')):
            os.system('mkdir "%s"' % os.path.join(MANAGED_FOLDER, 'Metadata', 'Movies'))
        if not os.path.isdir(os.path.join(MANAGED_FOLDER, 'Metadata', 'TV')):
            os.system('mkdir "%s"' % os.path.join(MANAGED_FOLDER, 'Metadata', 'TV'))

        # Open main menu
        self.view()

    def view(self):
        ''' displays main menu and leads to other modules '''
        #TODO: fix update library to only update path
        #TODO: view by show title
        #TODO: remove extraneous tv show folders in Metadata
        #TODO: add all items with metadata
        #?TODO: add all from here
        #?TODO: view all
        #TODO: rebuild managed list (remove all items, then re-add new instance of ContentItem)
        #TODO: add parameter for location in list -
        #   useful when returning here after doing something on an item
        #   (preselct is broken when pressing cancel)
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
