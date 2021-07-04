#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module gets called from the context menu item "Sync directory to library" (32001).

The purpose is to stage all movies/tvshows in the current directory, and update database.
"""

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

from resources.lib.utils import entrypoint
from resources.lib.utils import notification
from resources.lib.utils import getlocalizedstring

from resources.lib.database import Database
from resources.lib.progressbar import ProgressBar

from resources.lib.menus.synced import SyncedMenu

@entrypoint
def main():
    """Main entrypoint for context menu item."""
    sync_type = False
    file = xbmc.getInfoLabel('Container.FolderPath')
    label = xbmc.getInfoLabel('Container.FolderName')
    STR_CHOOSE_CONTENT_TYPE = getlocalizedstring(32164)
    OPTIONS = {
        32160: 'all_items',
        32161: 'movie',
        32162: 'tvshow',
        32167: 'filter',
        32157: 'cancel'
    }
    selection = xbmcgui.Dialog().select(
        heading=STR_CHOOSE_CONTENT_TYPE,
        list=[getlocalizedstring(x) for x in OPTIONS],
        useDetails=False,
        preselect=False
    )
    if selection == 'cancel':
        STR_NOT_SELECTED = getlocalizedstring(32158)
        notification(STR_NOT_SELECTED, 4000)
    else:
        sync_type = OPTIONS[list(OPTIONS.keys())[selection]]
        if sync_type:
            syncedmenu = SyncedMenu(
                database=Database(),
                progressdialog=ProgressBar()
            )
            syncedmenu.add_all_items_in_directory(
                sync_type,
                label,
                file
            )


if __name__ == '__main__':
    main()
