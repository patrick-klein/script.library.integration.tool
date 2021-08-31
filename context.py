#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Add selected item to library.

This module gets called from the context menu item "" (32000).
The purpose is to stage the currently selected movie/tvshow, and update synced directories.
"""

import sys

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

from resources.lib.database import Database
from resources.lib.progressbar import ProgressBar
from resources.lib.menus.synced import SyncedMenu

from resources.lib.utils import re_search
from resources.lib.utils import entrypoint
from resources.lib.utils import notification
from resources.lib.utils import title_with_color
from resources.lib.utils import getstring

STR_IS_A_MOVIE = getstring(32155)
STR_IS_A_SHOW = getstring(32156)
STR_CANCEL_RED = getstring(32157)
STR_NOT_SELECTED = getstring(32163)
STR_CHOOSE_CONTENT_TYPE = getstring(32159)

# possible values ​​that content can have
LIST_TYPE_SERIES = ['series',
                    'directory',
                    'show',
                    'browse',
                    'root',
                    'mode=102',
                    'mode=ondemand',
                    'mode=series']
LIST_TYPE_MOVIES = ['movie',
                    'PlayVideo',
                    'play&_play',
                    'mode=103',
                    'type=movies']


@entrypoint
def main():
    """Main entrypoint for context menu item."""
    title = sys.listitem.getLabel()  # pylint: disable=E1101
    year = xbmc.getInfoLabel('ListItem.Year')
    year = int(year) if year else False
    file = sys.listitem.getPath()  # pylint: disable=E1101
    STR_FORMED_TYPE_OF_CONTENT = '%s - %s' % (
        title_with_color(label=title, year=year),
        STR_CHOOSE_CONTENT_TYPE
    )
    lines = [
        STR_IS_A_MOVIE,
        STR_IS_A_SHOW,
        STR_CANCEL_RED
    ]
    selection = xbmcgui.Dialog().select(
        STR_FORMED_TYPE_OF_CONTENT,
        lines
    )
    selection = lines[selection]
    if selection:
        syncedmenu = SyncedMenu(
            database=Database(),
            progressdialog=ProgressBar()
        )
        # Call corresponding method
        if selection == STR_IS_A_MOVIE:
            if re_search(file, LIST_TYPE_MOVIES):
                syncedmenu.add_single_movie(
                    title=title,
                    year=year,
                    file=file
                )
        elif selection == STR_IS_A_SHOW:
            if re_search(file, LIST_TYPE_SERIES):
                syncedmenu.add_single_tvshow(
                    title=title,
                    year=year,
                    file=file
                )
        elif selection == STR_CANCEL_RED:
            xbmc.sleep(300)
            notification(getstring(32158))
        else:
            xbmc.sleep(300)
            notification('%s %s' % (
                title_with_color(label=title, year=year),
                STR_NOT_SELECTED
            )
            )


if __name__ == '__main__':
    main()
