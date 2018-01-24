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

from contentitem import MovieItem, EpisodeItem
from utils import get_items, save_items, log_msg

class Synced(object):
    '''
    provides windows for displaying synced directories,
    and tools for managing them and updating their contents
    '''

    def __init__(self, mainmenu):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')
        self.mainmenu = mainmenu
        self.synced_dirs = get_items('synced.pkl')

    def view(self):
        '''
        displays all synced directories, which are selectable and lead to options.
        also provides additional options at bottom of menu
        '''
        #TODO: update only movies or tvshows
        #TODO: sort
        #TODO: show title for single movie or tvshow
        STR_UPDATE_ALL = self.addon.getLocalizedString(32081)
        STR_REMOVE_ALL = self.addon.getLocalizedString(32082)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_SYNCED_DIRECTORIES = self.addon.getLocalizedString(32128)
        STR_NO_SYNCED_DIRS = self.addon.getLocalizedString(32120)
        if not self.synced_dirs:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_SYNCED_DIRS)
            return self.mainmenu.view()
        lines = ['%s - [I]%s[/I]'%(self.localize_type(x['mediatype']), x['dir']) \
            for x in self.synced_dirs]
        lines += [STR_UPDATE_ALL, STR_REMOVE_ALL, STR_BACK]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(
            self.STR_ADDON_NAME, STR_SYNCED_DIRECTORIES), lines)
        if not ret < 0:
            if ret < len(self.synced_dirs):   # managed item
                for i, x in enumerate(self.synced_dirs):
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
        else:
            return self.mainmenu.view()

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
        else:
            return mediatype

    def options(self, item):
        ''' provides options for a single synced directory in a dialog window '''
        #TODO: remove all from plugin
        STR_REMOVE = self.addon.getLocalizedString(32017)
        STR_SYNCED_DIR_OPTIONS = self.addon.getLocalizedString(32085)
        STR_BACK = self.addon.getLocalizedString(32011)
        lines = [STR_REMOVE, STR_BACK]
        ret = xbmcgui.Dialog().select('{0} - {1} - {2}'.format(
            self.STR_ADDON_NAME, STR_SYNCED_DIR_OPTIONS, item['dir']), lines)
        if not ret < 0:
            if lines[ret] == STR_REMOVE:
                self.synced_dirs.remove(item)
                save_items('synced.pkl', self.synced_dirs)
                return self.view()
            elif lines[ret] == STR_BACK:
                return self.view()
        else:
            return self.view()

    def remove_all(self):
        ''' removes all synced directories '''
        STR_REMOVE_ALL_SYNCED_DIRS = self.addon.getLocalizedString(32086)
        STR_ALL_SYNCED_DIRS_REMOVED = self.addon.getLocalizedString(32087)
        STR_ARE_YOU_SURE = self.addon.getLocalizedString(32088)
        if xbmcgui.Dialog().yesno('{0} - {1}'.format(
                self.STR_ADDON_NAME, STR_REMOVE_ALL_SYNCED_DIRS), STR_ARE_YOU_SURE):
            self.synced_dirs = []
            save_items('synced.pkl', self.synced_dirs)
            xbmc.executebuiltin(
                'Notification("{0}", "{1}")'.format(
                    self.STR_ADDON_NAME, STR_ALL_SYNCED_DIRS_REMOVED))

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
        STR_GETTING_ALL_ITEMS_FROM_SYNCED_DIRS = self.addon.getLocalizedString(32089)
        STR_FINDING_ITEMS_TO_REMOVE_FROM_MANAGED = self.addon.getLocalizedString(32090)
        STR_REMOVING_ITEMS_FROM_STAGED = self.addon.getLocalizedString(32091)
        STR_FINDING_ITEMS_TO_ADD = self.addon.getLocalizedString(32092)
        STR_i_TO_REMOVE_i_TO_STAGE_PROCEED = self.addon.getLocalizedString(32093)
        STR_REMOVING_ITEMS = self.addon.getLocalizedString(32094)
        STR_STAGIN_ITEMS = self.addon.getLocalizedString(32095)
        STR_ALL_ITEMS_UPTODATE = self.addon.getLocalizedString(32121)
        STR_SUCCESS = self.addon.getLocalizedString(32122)

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(self.STR_ADDON_NAME)

        # get current items in all directories
        pDialog.update(0, line1=STR_GETTING_ALL_ITEMS_FROM_SYNCED_DIRS)
        # get blocked lists ready
        blocked_items = get_items('blocked.pkl')
        blocked_movies = [x['label'] for x in blocked_items if x['type'] == 'movie']
        blocked_episodes = [x['label'] for x in blocked_items if x['type'] == 'episode']
        blocked_shows = [x['label'] for x in blocked_items if x['type'] == 'tvshow']
        blocked_keywords = [x['label'].lower() for x in blocked_items if x['type'] == 'keyword']
        dir_items = []
        for synced_dir in self.synced_dirs:
            pDialog.update(0, line2=synced_dir['dir'])
            # directory is just a path to a single movie
            if synced_dir['mediatype'] == 'single-movie':
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
                if synced_dir['mediatype'] == 'single-tvshow':
                    # check every episode in results
                    for ditem in synced_dir_items:
                        # need to check episode against blocklists
                        label = ditem['label']
                        if label in blocked_episodes or \
                            any(x in label.lower() for x in blocked_keywords):
                            continue
                        # add formatted item
                        ditem['mediatype'] = 'tvshow'
                        ditem['show_title'] = synced_dir['label']
                        dir_items.append(ditem)
                # directory is a path to list of movies
                elif synced_dir['mediatype'] == 'movie':
                    # check every movie in results
                    for ditem in synced_dir_items:
                        # skip if blocked
                        label = ditem['label']
                        if label in blocked_movies \
                            or any(x in label.lower() for x in blocked_keywords):
                            continue
                        # add tag to items
                        ditem['mediatype'] = 'movie'
                        dir_items.append(ditem)
                # dirctory is a path to a list of tv shows
                elif synced_dir['mediatype'] == 'tvshow':
                    # check every tvshow in list
                    for ditem in synced_dir_items:
                        show_title = ditem['label']
                        # check show_title against blocklists
                        if show_title in blocked_shows or \
                            any(x in show_title.lower() for x in blocked_keywords):
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
                            if label in blocked_episodes \
                            or any(x in label.lower() for x in blocked_keywords):
                                continue
                            # add formatted item
                            shitem['mediatype'] = 'tvshow'
                            shitem['show_title'] = show_title
                            dir_items.append(shitem)
                        pDialog.update(0, line3=' ')
            pDialog.update(0, line2=' ')

        # find managed_items not in dir_items, and prepare to remove
        pDialog.update(0, line1=STR_FINDING_ITEMS_TO_REMOVE_FROM_MANAGED)
        managed_items = get_items('managed.pkl')
        dir_paths = [x['file'] for x in dir_items]
        items_to_remove = []
        for item in managed_items:
            if item.get_path() not in dir_paths:
                pDialog.update(0, line2=item.get_title())
                items_to_remove.append(item)
            pDialog.update(0, line2=' ')

        # remove them from staged also (can do that immediately)
        pDialog.update(0, line1=STR_REMOVING_ITEMS_FROM_STAGED)
        staged_items = get_items('staged.pkl')
        for item in staged_items:
            if item.get_path() not in dir_paths:
                pDialog.update(0, line2=item.get_title())
                item.remove_from_staged()
            pDialog.update(0, line2=' ')

        # find dir_items not in managed_items or staged_items, and prepare to add
        pDialog.update(0, line1=STR_FINDING_ITEMS_TO_ADD)
        managed_paths = [x.get_path() for x in managed_items]
        staged_items = get_items('staged.pkl')
        staging_paths = [x.get_path() for x in staged_items]
        items_to_stage = []
        for ditem in dir_items:
            label = ditem['label']
            path = ditem['file']
            mediatype = ditem['mediatype']
            pDialog.update(0, line2=label)
            # don't prepare items that are already staged or managed
            if path in managed_paths or path in staging_paths:
                continue
            if mediatype == 'movie':
                item = MovieItem(path, label, mediatype)
            elif mediatype == 'tvshow':
                item = EpisodeItem(path, label, mediatype, ditem['show_title'])
            items_to_stage.append(item)
            staging_paths.append(ditem['file'])
        pDialog.update(0, line2=' ')

        # prompt user to remove & stage
        num_to_remove = len(items_to_remove)
        num_to_stage = len(items_to_stage)
        if num_to_remove > 0 or num_to_stage > 0:
            proceed = xbmcgui.Dialog().yesno(
                self.STR_ADDON_NAME, STR_i_TO_REMOVE_i_TO_STAGE_PROCEED \
                % (num_to_remove, num_to_stage))
            if proceed:
                pDialog.update(0, line1=STR_REMOVING_ITEMS)
                for item in items_to_remove:
                    log_msg('Removing from library: %s' % item.get_title(), xbmc.LOGNOTICE)
                    pDialog.update(0, line2=item.get_title())
                    item.remove_from_library()
                    pDialog.update(0, line2=' ')
                pDialog.update(0, line1=STR_STAGIN_ITEMS)
                if num_to_stage > 0:
                    staged_items += items_to_stage
                    save_items('staged.pkl', staged_items)
                    log_msg('Updated staged file with items from synced directories.')
                xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_SUCCESS)
        else:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_ALL_ITEMS_UPTODATE)
        pDialog.close()
