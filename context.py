#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This module gets called from the context menu item "Add selected item to library" (32000).
The purpose is to stage the currently selected movie/tvshow, and update synced directories.
'''
import sys

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

import resources.lib.utils as utils
from resources.lib.menus.synced import SyncedMenu

@utils.entrypoint
def main():
    ''' Main entrypoint for context menu item '''
    # is more simple and fast ask user about type, many addons don't give this info
    label = sys.listitem.getLabel()  # pylint: disable=E1101
    year = xbmc.getInfoLabel('ListItem.Year')

    selected_path = sys.listitem.getPath() # pylint: disable=E1101
    STR_CHOOSE_CONTENT_TYPE = utils.getlocalizedstring(32100)
    # Using the Dialog().select method is better as it allows the user to cancel if they want,
    #  and we can add more options if needed.
    typeofcontent = xbmcgui.Dialog().select(
        STR_CHOOSE_CONTENT_TYPE, [
            'It is a Movie',
            'It is a Show',
            '[COLOR red][B]Cancel[/B][/COLOR]'
            ]
        )
    # Call corresponding method
    if typeofcontent == 0:
        SyncedMenu().sync_single_movie(title=label, year=year, link_stream_path=selected_path)
    elif typeofcontent == 1:
        SyncedMenu().sync_single_tvshow(title=label, year=year, link_stream_path=selected_path)
    elif typeofcontent == -1 or 2:
        xbmc.sleep(200)
        utils.notification('Type of content not selected, Try again.')

if __name__ == '__main__':
    main()
