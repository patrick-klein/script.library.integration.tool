#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This module contains the class Blocked,
which provide dialog windows and tools for manged blocked items
'''

import xbmcgui
import xbmcaddon

from utils import get_items, save_items

class Blocked(object):
    '''
    provides windows for displaying blocked items,
    and tools for managing them
    '''

    def __init__(self, mainmenu):
        self.addon = xbmcaddon.Addon()
        self.STR_ADDON_NAME = self.addon.getAddonInfo('name')
        self.mainmenu = mainmenu
        self.blocked_items = get_items('blocked.pkl')

    def view(self):
        '''
        displays all blocked items, which are selectable and lead to options.
        also provides additional options at bottom of menu
        '''
        #?TODO: change movie/episode to just path
        #?TODO: make blocked episode match on episode & show
        #TODO: add types: plugin, path
        STR_ADD_KEYWORD = self.addon.getLocalizedString(32097)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_BLOCKED_ITEMS = self.addon.getLocalizedString(32098)
        STR_NO_BLOCKED_ITEMS = self.addon.getLocalizedString(32119)
        if not self.blocked_items:
            xbmcgui.Dialog().ok(self.STR_ADDON_NAME, STR_NO_BLOCKED_ITEMS)
            return self.mainmenu.view()
        lines = ['{0} - [B]{1}[/B]'.format(self.localize_type(x['type']), x['label']) \
            for x in self.blocked_items]
        lines, self.blocked_items = (list(t) for t in zip(*sorted(zip(lines, self.blocked_items),
                                                                  key=lambda x: x[0].lower())))
        lines += [STR_ADD_KEYWORD, STR_BACK]
        ret = xbmcgui.Dialog().select('{0} - {1}'.format(
            self.STR_ADDON_NAME, STR_BLOCKED_ITEMS), lines)
        if not ret < 0:
            if ret < len(self.blocked_items):   # managed item
                for i, x in enumerate(self.blocked_items):
                    if ret == i:
                        return self.options(x)
            elif lines[ret] == STR_ADD_KEYWORD:
                self.add_keyword()
                return self.view()
            elif lines[ret] == STR_BACK:
                return self.mainmenu.view()
        else:
            return self.mainmenu.view()

    def add_keyword(self):
        ''' prompts user for keyword, and adds it to blocked list '''
        input_ret = xbmcgui.Dialog().input("Blocked keyword")
        if input_ret:
            self.blocked_items.append({'type':'keyword', 'label':input_ret})
            save_items('blocked.pkl', self.blocked_items)

    def options(self, item):
        ''' provides options for a single blocked item in a dialog window '''
        STR_REMOVE = self.addon.getLocalizedString(32017)
        STR_BACK = self.addon.getLocalizedString(32011)
        STR_BLOCKED_ITEM_OPTIONS = self.addon.getLocalizedString(32099)
        lines = [STR_REMOVE, STR_BACK]
        ret = xbmcgui.Dialog().select('{0} - {1} - {2}'.format(
            self.STR_ADDON_NAME, STR_BLOCKED_ITEM_OPTIONS, item['label']), lines)
        if not ret < 0:
            if lines[ret] == STR_REMOVE:
                self.blocked_items.remove(item)
                save_items('blocked.pkl', self.blocked_items)
                return self.view()
            elif lines[ret] == STR_BACK:
                return self.view()
        else:
            return self.view()

    def localize_type(self, mediatype):
        ''' localizes tages used for identifying mediatype '''
        if mediatype == 'movie':      # Movie
            return self.addon.getLocalizedString(32102)
        elif mediatype == 'tvshow':   # TV Show
            return self.addon.getLocalizedString(32101)
        elif mediatype == 'keyword':  # Keyword
            return self.addon.getLocalizedString(32113)
        elif mediatype == 'episode':  # Episode
            return self.addon.getLocalizedString(32114)
        else:
            return mediatype
