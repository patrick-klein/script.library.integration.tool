#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This module gets called from the context menu item "Sync directory to library" (32001).
The purpose is to stage all movies/tvshows in the current directory, and update database
'''

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

import resources.lib.utils as utils
from resources.lib.menus.synced import SyncedMenu

STR_SYNC_ALL_ITEMS = utils.getlocalizedstring(32160)
STR_SYNC_ONLY_MOVIES = utils.getlocalizedstring(32161)
STR_SYNC_ONLY_SHOWS = utils.getlocalizedstring(32162)
STR_CANCEL_RED = utils.getlocalizedstring(32157)
STR_NOT_SELECTED = utils.getlocalizedstring(32158)


@utils.entrypoint
def main():
    ''' Main entrypoint for context menu item '''
    sync_type = False
    dir_path = xbmc.getInfoLabel('Container.FolderPath')
    dir_label = xbmc.getInfoLabel('Container.FolderName')
    # Get content type
    STR_CHOOSE_CONTENT_TYPE = utils.getlocalizedstring(32164)

    lines = [
        STR_SYNC_ALL_ITEMS,
        STR_SYNC_ONLY_MOVIES,
        STR_SYNC_ONLY_SHOWS,
        STR_CANCEL_RED
    ]
    typeofcontent = xbmcgui.Dialog().select(
        STR_CHOOSE_CONTENT_TYPE,
        lines
        )
    # Call corresponding method
    selection = lines[typeofcontent]
    if selection:
        if selection == STR_SYNC_ALL_ITEMS:
            sync_type = 'all_items'
        elif selection == STR_SYNC_ONLY_MOVIES:
            sync_type = 'movie'
        elif selection == STR_SYNC_ONLY_SHOWS:
            sync_type = 'tvshow'
        elif selection == STR_CANCEL_RED:
            utils.notification(STR_NOT_SELECTED, 4000)

    if sync_type:
        try:
            SyncedMenu().sync_all_items_in_directory(sync_type, dir_label, dir_path)
        except Exception as genericexception:
            # TODO: A generic except, in furure, can be updated
            raise genericexception


if __name__ == '__main__':
    main()
