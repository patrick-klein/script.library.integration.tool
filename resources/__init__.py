# /usr/bin/python
# -*- coding: utf-8 -*-

"""LIT initial module whith base variables used in all project."""

import xbmc
import xbmcaddon

# Get settings
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_VERSION = ADDON.getAddonInfo('version')

AUTO_ADD_MOVIES = ADDON.getSetting('auto_add_movies') == 'true'
AUTO_ADD_TVSHOWS = ADDON.getSetting('auto_add_tvshows') == 'true'
AUTO_CREATE_NFO_MOVIES = ADDON.getSetting('auto_create_nfo_movies') == 'true'
AUTO_CREATE_NFO_SHOWS = ADDON.getSetting('auto_create_nfo_shows') == 'true'
# USE_SHOW_ARTWORK_SHOW = ADDON.getSetting('use_show_artwork_show') == 'true'

IN_DEVELOPMENT = ADDON.getSetting('in_development') == 'true'
RECURSION_LIMIT = int(ADDON.getSetting('recursion_limit'))

USING_CUSTOM_MANAGED_FOLDER = ADDON.getSetting('custom_managed_folder') == 'true'

# Define other constants
DEFAULT_LOG_LEVEL = xbmc.LOGINFO if IN_DEVELOPMENT else xbmc.LOGDEBUG
