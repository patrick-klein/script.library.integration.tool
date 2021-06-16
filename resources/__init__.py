# /usr/bin/python
# -*- coding: utf-8 -*-

from os.path import join

import xbmc # pylint: disable=import-error
import xbmcvfs # pylint: disable=import-error
import xbmcaddon # pylint: disable=import-error

# Get settings
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_VERSION = ADDON.getAddonInfo('version')
AUTO_ADD_MOVIES = ADDON.getSetting('auto_add_movies')
AUTO_ADD_TVSHOWS = ADDON.getSetting('auto_add_tvshows')
IN_DEVELOPMENT = ADDON.getSetting('in_development') == 'true'
RECURSION_LIMIT = int(ADDON.getSetting('recursion_limit'))
USE_SHOW_ARTWORK = ADDON.getSetting('use_show_artwork') == 'true'
USING_CUSTOM_MANAGED_FOLDER = ADDON.getSetting('custom_managed_folder') == 'true'
USING_CUSTOM_METADATA_FOLDER = ADDON.getSetting('custom_metadata_folder') == 'true'

if USING_CUSTOM_MANAGED_FOLDER:
    MANAGED_FOLDER = ADDON.getSetting('managed_folder')
else:
    MANAGED_FOLDER = xbmcvfs.translatePath('special://userdata/addon_data/{}/'.format(ADDON_ID))
if USING_CUSTOM_METADATA_FOLDER:
    METADATA_FOLDER = ADDON.getSetting('metadata_folder')
else:
    METADATA_FOLDER = join(MANAGED_FOLDER, 'Metadata')


# Enum values in settings
NEVER = '0'
ALWAYS = '1'
WITH_EPID = '1'
WITH_METADATA = '2'

# Define other constants
DEFAULT_LOG_LEVEL = xbmc.LOGINFO if IN_DEVELOPMENT else xbmc.LOGDEBUG

DATABASE_FILE = join(MANAGED_FOLDER, 'managed.db')
