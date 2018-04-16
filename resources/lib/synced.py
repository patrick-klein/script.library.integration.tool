#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This module contains the class Synced,
which provide dialog windows and tools for manged synced directories
'''

import simplejson as json
import xbmc
import xbmcgui
import xbmcaddon

from utils import log_decorator, notification
from database_handler import DB_Handler

class Synced(object):
    '''
    provides windows for displaying synced directories,
    and tools for managing them and updating their contents
    '''

    def __init__(self, mainmenu):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')
        self.mainmenu = mainmenu
        self.dbh = DB_Handler()

    @log_decorator
    def view(self):
        '''
        displays all synced directories, which are selectable and lead to options.
        also provides additional options at bottom of menu
        '''
        #TODO: update only movies or tvshows
        STR_UPDATE_ALL = self.addon.getLocalizedString(32081)
        STR_REMOVE_ALL = self.addon.getLocalizedString(32082)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_SYNCED_DIRECTORIES = self.addon.getLocalizedString(32128)
        STR_NO_SYNCED_DIRS = self.addon.getLocalizedString(32120)
        synced_dirs = self.dbh.get_synced_dirs()
        if not synced_dirs:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_SYNCED_DIRS)
            return self.mainmenu.view()
        lines = ['[B]%s[/B] - %s - [I]%s[/I]' % (x['label'], \
            self.localize_type(x['type']), x['dir']) for x in synced_dirs]
        lines += [STR_UPDATE_ALL, STR_REMOVE_ALL, STR_BACK]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(
            self.STR_ADDON_NAME, STR_SYNCED_DIRECTORIES), lines)
        if not ret < 0:
            if ret < len(synced_dirs):   # managed item
                for i, x in enumerate(synced_dirs):
                    if ret == i:
                        return self.options(x)
            elif lines[ret] == STR_UPDATE_ALL:
                self.update_all()
                return self.mainmenu.view()
            elif lines[ret] == STR_REMOVE_ALL:
                self.remove_all()
                return self.mainmenu.view()
            elif lines[ret] == STR_BACK:
                return self.mainmenu.view()
        return self.mainmenu.view()

    @log_decorator
    def localize_type(self, mediatype):
        ''' localizes tages used for identifying mediatype '''
        if mediatype == 'movie':      # Movies
            return self.addon.getLocalizedString(32109)
        elif mediatype == 'tvshow':   # TV Shows
            return self.addon.getLocalizedString(32108)
        elif mediatype == 'single-movie': # Single Movie
            return self.addon.getLocalizedString(32116)
        elif mediatype == 'single-tvshow':  # Single TV Show
            return self.addon.getLocalizedString(32115)
        return mediatype

    @log_decorator
    def options(self, item):
        ''' provides options for a single synced directory in a dialog window '''
        #TODO: remove all from plugin
        #TODO: rename label
        STR_REMOVE = self.addon.getLocalizedString(32017)
        STR_SYNCED_DIR_OPTIONS = self.addon.getLocalizedString(32085)
        STR_BACK = self.addon.getLocalizedString(32011)
        lines = [STR_REMOVE, STR_BACK]
        ret = xbmcgui.Dialog().select('{0} - {1} - {2}'.format(
            self.STR_ADDON_NAME, STR_SYNCED_DIR_OPTIONS, item['label']), lines)
        if not ret < 0:
            if lines[ret] == STR_REMOVE:
                self.dbh.remove_synced_dir(item['dir'])
                return self.view()
            elif lines[ret] == STR_BACK:
                return self.view()
        return self.view()

    @log_decorator
    def remove_all(self):
        ''' removes all synced directories '''
        STR_REMOVE_ALL_SYNCED_DIRS = self.addon.getLocalizedString(32086)
        STR_ALL_SYNCED_DIRS_REMOVED = self.addon.getLocalizedString(32087)
        STR_ARE_YOU_SURE = self.addon.getLocalizedString(32088)
        if xbmcgui.Dialog().yesno('{0} - {1}'.format(
                self.STR_ADDON_NAME, STR_REMOVE_ALL_SYNCED_DIRS), STR_ARE_YOU_SURE):
            self.dbh.remove_all_synced_dirs()
            notification(STR_ALL_SYNCED_DIRS_REMOVED)

    @log_decorator
    def update_all(self):
        '''
        gets all items from synced directories,
        then finds unavailable items to remove from managed,
        and new items to stage
        '''
        #TODO: wait until after confirmation to remove staged items also
        #TODO: bugfix: single-movies won't actually get removed if they become unavailable
        #       maybe load parent dir and check for path or label?  it would be slower though
        #TODO: bugfix: unicode error when comparing some blocked titles
        #TODO: option to only update specified or managed items
        #TODO: option to add update frequencies for specific directories (i.e. weekly/monthly/etc.)
        STR_GETTING_ALL_ITEMS_FROM_SYNCED_DIRS = self.addon.getLocalizedString(32089)
        STR_FINDING_ITEMS_TO_REMOVE_FROM_MANAGED = self.addon.getLocalizedString(32090)
        STR_REMOVING_ITEMS_FROM_STAGED = self.addon.getLocalizedString(32091)
        STR_FINDING_ITEMS_TO_ADD = self.addon.getLocalizedString(32092)
        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED = self.addon.getLocalizedString(32093)
        STR_REMOVING_ITEMS = self.addon.getLocalizedString(32094)
        STR_STAGING_ITEMS = self.addon.getLocalizedString(32095)
        STR_ALL_ITEMS_UPTODATE = self.addon.getLocalizedString(32121)
        STR_SUCCESS = self.addon.getLocalizedString(32122)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME)

        # get current items in all directories
        pDialog.update(0, line1=STR_GETTING_ALL_ITEMS_FROM_SYNCED_DIRS)
        synced_dirs = self.dbh.get_synced_dirs()
        dir_items = []
        for synced_dir in synced_dirs:
            pDialog.update(0, line2=synced_dir['dir'])
            # directory is just a path to a single movie
            if synced_dir['type'] == 'single-movie':
                # add formatted single-movie items to dir_items (no need to check for blocked)
                dir_items.append(
                    {'file':synced_dir['dir'], 'label':synced_dir['label'], 'mediatype':'movie'})
            else:
                # need to load results for other mediatypes
                result = json.loads(xbmc.executeJSONRPC(
                    '{"jsonrpc": "2.0", "method": "Files.GetDirectory", \
                    "params": {"directory":"%s"}, "id": 1}' % synced_dir['dir']))
                # skip if results don't load
                if not (result.has_key('result') and result["result"].has_key('files')):
                    continue
                synced_dir_items = result["result"]["files"]
                # directory is a path to a tv show folder
                if synced_dir['type'] == 'single-tvshow':
                    # check every episode in results
                    for ditem in synced_dir_items:
                        # need to check episode against blocklists
                        label = ditem['label']
                        if self.dbh.check_blocked(label, 'episode'):
                            continue
                        # add formatted item
                        ditem['mediatype'] = 'tvshow'
                        ditem['show_title'] = synced_dir['label']
                        dir_items.append(ditem)
                # directory is a path to list of movies
                elif synced_dir['type'] == 'movie':
                    # check every movie in results
                    for ditem in synced_dir_items:
                        # skip if blocked
                        label = ditem['label']
                        if self.dbh.check_blocked(label, 'movie'):
                            continue
                        # add tag to items
                        ditem['mediatype'] = 'movie'
                        dir_items.append(ditem)
                # dirctory is a path to a list of tv shows
                elif synced_dir['type'] == 'tvshow':
                    # check every tvshow in list
                    for ditem in synced_dir_items:
                        show_title = ditem['label']
                        # check show_title against blocklists
                        if self.dbh.check_blocked(show_title, 'tvshow'):
                            continue
                        # load results if show isn't blocked
                        pDialog.update(0, line3=show_title)
                        show_path = ditem['file']
                        show_result = json.loads(xbmc.executeJSONRPC(
                            '{"jsonrpc": "2.0", "method": "Files.GetDirectory", \
                            "params": {"directory":"%s"}, "id": 1}' % show_path))
                        # skip if results don't load
                        if not (show_result.has_key('result') \
                            and show_result["result"].has_key('files')):
                            pDialog.update(0, line3=' ')
                            continue
                        # check every episode in show
                        show_items = show_result["result"]["files"]
                        for shitem in show_items:
                            # need to check episode against blocklists
                            label = shitem['label']
                            if self.dbh.check_blocked(label, 'episode'):
                                continue
                            # add formatted item
                            shitem['mediatype'] = 'tvshow'
                            shitem['show_title'] = show_title
                            dir_items.append(shitem)
                        pDialog.update(0, line3=' ')
            pDialog.update(0, line2=' ')

        # find managed paths not in dir_items, and prepare to remove
        pDialog.update(0, line1=STR_FINDING_ITEMS_TO_REMOVE_FROM_MANAGED)
        managed_items = self.dbh.get_content_items('managed')
        dir_paths = [x['file'] for x in dir_items]
        paths_to_remove = []
        for item in managed_items:
            if item.get_path() not in dir_paths:
                pDialog.update(0, line2=item.get_title())
                paths_to_remove.append(item.get_path())
            pDialog.update(0, line2=' ')

        # remove them from staged also (can do that immediately)
        pDialog.update(0, line1=STR_REMOVING_ITEMS_FROM_STAGED)
        staged_items = self.dbh.get_content_items('staged')
        for item in staged_items:
            if item.get_path() not in dir_paths:
                pDialog.update(0, line2=item.get_title())
                self.dbh.remove_content_item(item.get_path())
            pDialog.update(0, line2=' ')

        # find dir_items not in managed_items or staged_items, and prepare to add
        pDialog.update(0, line1=STR_FINDING_ITEMS_TO_ADD)
        items_to_stage = []
        for ditem in dir_items:
            path = ditem['file']
            # don't prepare items that are already staged or managed
            if self.dbh.path_exists(path):
                continue
            label = ditem['label']
            pDialog.update(0, line2=label)
            mediatype = ditem['mediatype']
            if mediatype == 'movie':
                item = (path, label, mediatype)
            elif mediatype == 'tvshow':
                item = (path, label, mediatype, ditem['show_title'])
            items_to_stage.append(item)
        pDialog.update(0, line2=' ')

        # prompt user to remove & stage
        num_to_remove = len(paths_to_remove)
        num_to_stage = len(items_to_stage)
        if num_to_remove > 0 or num_to_stage > 0:
            proceed = xbmcgui.Dialog().yesno(
                self.STR_ADDON_NAME, STR_i_TO_REMOVE_i_TO_STAGE_PROCEED \
                % (num_to_remove, num_to_stage))
            if proceed:
                pDialog.update(0, line1=STR_REMOVING_ITEMS)
                for path in paths_to_remove:
                    item = self.dbh.load_item(path)
                    pDialog.update(0, line2=item.get_title())
                    item.remove_from_library()
                    item.delete()
                    pDialog.update(0, line2=' ')
                pDialog.update(0, line1=STR_STAGING_ITEMS)
                for item in items_to_stage:
                    pDialog.update(0, line2=item[1])
                    self.dbh.add_content_item(*item)
                    pDialog.update(0, line2=' ')
                xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_SUCCESS)
        else:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        pDialog.close()
