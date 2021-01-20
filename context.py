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

def label_with_year(title, year):
    # Amazon dont return year for all items, year will be added only if exist
    if len(year) == 4:
        return ('%s (%s)' % (title, year))
    else:
        return ('%s' % title)
        pass

def get_type_from_dir(current_dir, selected_path):
    # this is not my favorite path, but in testing it works in all cases
    results = utils.execute_json_rpc('Files.GetDirectory', directory=current_dir)

    for item in results['result']['files']:
        if item['file'] == selected_path:
            return item['type']

@utils.entrypoint
def main():
    ''' Main entrypoint for context menu item '''
    # kodi 19, the index of item maybe cam be usefull to get info
    # current_index_item = xbmc.getInfoLabel('ListItem.CurrentItem')
    # 
    label = sys.listitem.getLabel().decode('utf-8')  # pylint: disable=E1101
    year = xbmc.getInfoLabel('ListItem.Year')

    current_dir = xbmc.getInfoLabel('Container.FolderPath')
    selected_path = sys.listitem.getPath()  # pylint: disable=E1101
    container_type = get_type_from_dir(current_dir, selected_path)
        
    # Get content type
    # ATENTION: the inclusion of year is a test, Netflix and Amazon VOD works in tests to give year for shows and movies
    # but can not work in all contents

    # UPDATE: not all shows from amazon return year, now will be staged with year if exist

    if container_type == 'movie':
        typeofcontent = 0
        label = label_with_year(title=label, year=year)
    elif container_type == 'tvshow':
        typeofcontent = 1
        label = label_with_year(title=label, year=year)
    else:
        STR_CHOOSE_CONTENT_TYPE = utils.ADDON.getLocalizedString(32100)
        STR_MOVIE = utils.ADDON.getLocalizedString(32102)
        STR_TV_SHOW = utils.ADDON.getLocalizedString(32101)
        # Using the Dialog().select method is better as it allows the user to cancel if they want, and we can add more options if needed.
        typeofcontent = xbmcgui.Dialog().select(STR_CHOOSE_CONTENT_TYPE, ['It is a Movie', 'It is a Show', '[COLOR red][B]Cancel[/B][/COLOR]'])
        label = label_with_year(title=label, year=year)

    # Call corresponding method
    if typeofcontent == 0:
        SyncedMenu().sync_single_movie(label, selected_path)
    elif typeofcontent == 1:
        SyncedMenu().sync_single_tvshow(label, selected_path)
    elif typeofcontent == -1 or 2:
        xbmc.sleep(200)
        utils.notification('Type of content not selected, Try again.')
        pass

if __name__ == '__main__':
    main()
