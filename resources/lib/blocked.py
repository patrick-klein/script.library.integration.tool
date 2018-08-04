#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This module contains the class Blocked,
which provide dialog windows and tools for manged blocked items
'''

import xbmcaddon
import xbmcgui

import database_handler as db
import resources.lib.utils as utils

class BlockedItem(dict):
    '''  '''

    def __init__(self, value, blocked_type):
        super(BlockedItem, self).__init__()
        self['value'] = value
        self['type'] = blocked_type


class Blocked(object):
    '''
    provides windows for displaying blocked items,
    and tools for managing them
    '''

    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')
        self.dbh = db.DatabaseHandler()

    @utils.log_decorator
    def view(self):
        '''
        displays all blocked items, which are selectable and lead to options.
        also provides additional options at bottom of menu
        '''
        # TODO?: change blocked movie/episode to just blocked path
        # TODO?: make blocked episode match on both episode AND show
        # TODO: add blocked types: plugin, path
        # TODO: add blocked keywords, let you choose type
        # TODO: intialize blocked list with known bad items
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_BLOCKED_ITEMS = self.addon.getLocalizedString(32098)
        STR_NO_BLOCKED_ITEMS = self.addon.getLocalizedString(32119)
        blocked_items = self.dbh.get_blocked_items()
        if not blocked_items:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_BLOCKED_ITEMS)
            return
        lines = ['{0} - [B]{1}[/B]'.format( \
            self.localize_type(x['type']), x['value']) for x in blocked_items]
        lines += [STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(self.STR_ADDON_NAME, STR_BLOCKED_ITEMS), lines
        )
        if ret >= 0:
            if ret < len(blocked_items):  # managed item
                for index, item in enumerate(blocked_items):
                    if ret == index:
                        self.options(item)
                        break
            elif lines[ret] == STR_BACK:
                return

    @utils.log_decorator
    def options(self, item):
        ''' provides options for a single blocked item in a dialog window '''
        STR_REMOVE = self.addon.getLocalizedString(32017)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_BLOCKED_ITEM_OPTIONS = self.addon.getLocalizedString(32099)
        lines = [STR_REMOVE, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(self.STR_ADDON_NAME, STR_BLOCKED_ITEM_OPTIONS, item['value']),
            lines
        )
        if ret >= 0:
            if lines[ret] == STR_REMOVE:
                self.dbh.remove_blocked(item['value'], item['type'])
                return self.view()
            elif lines[ret] == STR_BACK:
                return self.view()
        return self.view()

    def localize_type(self, mediatype):
        ''' localizes tages used for identifying mediatype '''
        if mediatype == 'movie':  # Movie
            return self.addon.getLocalizedString(32102)
        elif mediatype == 'tvshow':  # TV Show
            return self.addon.getLocalizedString(32101)
        elif mediatype == 'keyword':  # Keyword
            return self.addon.getLocalizedString(32113)
        elif mediatype == 'episode':  # Episode
            return self.addon.getLocalizedString(32114)
        return mediatype
