# /usr/bin/python
# -*- coding: utf-8 -*-

"""LIT initial module whith base variables used in all projetct."""

import xbmc  # pylint: disable=import-error
import xbmcaddon  # pylint: disable=import-error

# Get settings
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_VERSION = ADDON.getAddonInfo('version')
AUTO_ADD_MOVIES = ADDON.getSettingBool('auto_add_movies')
AUTO_ADD_TVSHOWS = ADDON.getSettingBool('auto_add_tvshows')
AUTO_CREATE_NFO_MOVIES = ADDON.getSettingBool('auto_create_nfo_movies')
AUTO_CREATE_NFO_SHOWS = ADDON.getSettingBool('auto_create_nfo_shows')
IN_DEVELOPMENT = ADDON.getSetting('in_development') == 'true'
RECURSION_LIMIT = int(ADDON.getSetting('recursion_limit'))
# USE_SHOW_ARTWORK_SHOW = ADDON.getSetting('use_show_artwork_show') == 'true'

USING_CUSTOM_MANAGED_FOLDER = ADDON.getSetting('custom_managed_folder') == 'true'

# Define other constants
DEFAULT_LOG_LEVEL = xbmc.LOGINFO if IN_DEVELOPMENT else xbmc.LOGDEBUG
