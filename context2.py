#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This module gets called from the context menu item "Sync directory to library" (32001).
The purpose is to stage all movies/tvshows in the current directory, and update database
'''

import xbmc
import xbmcgui

import resources.lib.utils as utils
from resources.lib.menus.synced import SyncedMenu


@utils.entrypoint
def main():
    ''' Main entrypoint for context menu item '''

    container_type = xbmc.getInfoLabel('Container.Content')
    dir_path = xbmc.getInfoLabel('Container.FolderPath')
    dir_label = xbmc.getInfoLabel('Container.FolderName')

    # Get content type
    if container_type == 'tvshows':
        content_type = "tvshow"
    elif container_type == 'movies':
        content_type = "movie"
    else:
        STR_CHOOSE_CONTENT_TYPE = utils.ADDON.getLocalizedString(32100)
        STR_MOVIE = utils.ADDON.getLocalizedString(32102)
        STR_TV_SHOW = utils.ADDON.getLocalizedString(32101)
        is_show = xbmcgui.Dialog().yesno(
            utils.ADDON_NAME, STR_CHOOSE_CONTENT_TYPE, yeslabel=STR_TV_SHOW, nolabel=STR_MOVIE
        )
        content_type = 'tvshow' if is_show else 'movie'

    from resources.lib.saveasjson import saveAsJson
    # Call corresponding method
    if content_type == 'movie':
        SyncedMenu().sync_movie_directory(dir_label, dir_path)
    elif content_type == 'tvshow':
        SyncedMenu().sync_tvshow_directory(dir_label, dir_path)


if __name__ == '__main__':
    main()
