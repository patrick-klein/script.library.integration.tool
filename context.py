#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This module gets called from the context menu item "Add selected item to library" (32000).
The purpose is to stage the currently selected movie/tvshow, and update synced directories.
'''

import sys

import xbmc
import xbmcgui

import resources.lib.utils as utils
from resources.lib.menus.synced import SyncedMenu


@utils.entrypoint
def main():
    ''' Main entrypoint for context menu item '''
    # container_type = xbmc.getInfoLabel('Container.Content')
    # label = sys.listitem.getLabel()  # pylint: disable=E1101
    path = sys.listitem.getPath()  # pylint: disable=E1101
    # 
    year = xbmc.getInfoLabel('ListItem.Year')
    # 
    # this method works, if is a show or a movie will be not empty
    tvshowtitle = xbmc.getInfoLabel('ListItem.TVShowTitle')
    movietitle = xbmc.getInfoLabel('ListItem.Title')

    # Get content type
    # ATENTION: the inclusion of year is a test, Netflix and Amazon VOD works in tests to give year for shows and movies
    # but can not work in all contents
    if len(tvshowtitle) > 0:
        content_type = 'tvshow'
        label = ('%s (%s)' % (tvshowtitle, year))
    elif len(movietitle) > 0:
        content_type = 'movie'
        label = ('%s (%s)' % (movietitle, year))
    else:
        STR_CHOOSE_CONTENT_TYPE = utils.ADDON.getLocalizedString(32100)
        STR_MOVIE = utils.ADDON.getLocalizedString(32102)
        STR_TV_SHOW = utils.ADDON.getLocalizedString(32101)
        is_show = xbmcgui.Dialog().yesno(
            utils.ADDON_NAME, STR_CHOOSE_CONTENT_TYPE, yeslabel=STR_TV_SHOW, nolabel=STR_MOVIE
        )
        content_type = 'tvshow' if is_show else 'movie'

    # Call corresponding method
    if content_type == 'movie':
        SyncedMenu().sync_single_movie(label, path)
    elif content_type == 'tvshow':
        SyncedMenu().sync_single_tvshow(label, path)


if __name__ == '__main__':
    main()
