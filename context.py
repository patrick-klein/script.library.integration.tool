#!/usr/bin/python
# -*- coding: utf-8 -*-

'''This module gets called from the context menu item "Add selected item to library" (32000).
The purpose is to stage the currently selected movie/tvshow, and update synced directories.'''

import sys

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

from resources.lib.database import Database
from resources.lib.menus.synced import SyncedMenu

from resources.lib.utils import re_search
from resources.lib.utils import entrypoint
from resources.lib.utils import notification
from resources.lib.utils import title_with_color
from resources.lib.utils import getlocalizedstring

STR_IS_A_MOVIE = getlocalizedstring(32155)
STR_IS_A_SHOW = getlocalizedstring(32156)
STR_CANCEL_RED = getlocalizedstring(32157)
STR_NOT_SELECTED = getlocalizedstring(32163)
STR_CHOOSE_CONTENT_TYPE = getlocalizedstring(32159)

# possible values ​​that content can have
LIST_TYPE_SERIES = ['series', 'directory', 'show', 'browse', 'root', 'mode=series']
LIST_TYPE_MOVIES = ['movie', 'PlayVideo', 'play&_play']

@entrypoint
def main():
    '''Main entrypoint for context menu item'''
    # is more simple and fast ask user about type, many addons don't give this info
    label = sys.listitem.getLabel()  # pylint: disable=E1101
    year = xbmc.getInfoLabel('ListItem.Year')
    # if year is False, load load_directory_items will use json year
    year = int(year) if year != '' else False
    file = sys.listitem.getPath() # pylint: disable=E1101
    STR_FORMED_TYPE_OF_CONTENT = '%s - %s' % (
        title_with_color(label=label, year=year), STR_CHOOSE_CONTENT_TYPE)
    # Using the Dialog().select method is better as
    # it allows the user to cancel if they want,
    # and we can add more options if needed.
    lines = [
        STR_IS_A_MOVIE,
        STR_IS_A_SHOW,
        STR_CANCEL_RED
    ]
    # I tried to add as many checks to determine the type,
    # maybe the dialog can be removed, but I prefer mater
    typeofcontent = xbmcgui.Dialog().select(
        STR_FORMED_TYPE_OF_CONTENT, lines
        )
    selection = lines[typeofcontent]
    if selection:
        syncedmenu = SyncedMenu(database=Database())
        # Call corresponding method
        if selection == STR_IS_A_MOVIE:
            if re_search(file, LIST_TYPE_MOVIES):
                syncedmenu.add_single_movie(
                    title=label,
                    year=year,
                    file=file
                )
        elif selection == STR_IS_A_SHOW:
            if re_search(file, LIST_TYPE_SERIES):
                syncedmenu.add_single_tvshow(
                    title=label,
                    year=year,
                    file=file
                )
        elif selection == STR_CANCEL_RED:
            xbmc.sleep(200)
            notification(getlocalizedstring(32158))
        else:
            notification(
                '%s %s' % (title_with_color(label=label,year=year),
                STR_NOT_SELECTED
                )
            )


if __name__ == '__main__':
    main()
