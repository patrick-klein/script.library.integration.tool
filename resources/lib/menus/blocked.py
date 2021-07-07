#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines the BlockedMenu class."""

import xbmcgui  # pylint: disable=import-error

from resources import ADDON_NAME
from resources.lib.log import logged_function
from resources.lib.utils import getstring


class BlockedMenu(object):
    """Provide windows for displaying blocked items and tools for managing them."""

    def __init__(self, database, progressdialog):
        """__init__ BlockedMenu."""
        self.database = database

    @logged_function
    def view(self):
        """
        Display all blocked items, which are selectable and lead to options.

        Also provides additional options at bottom of menu.
        """
        # TODO?: change blocked movie/episode to just blocked path
        # TODO?: make blocked episode match on both episode AND show
        # TODO: add blocked types: plugin, path
        # TODO: add blocked keywords, let you choose type
        # TODO: intialize blocked list with known bad items
        STR_BACK = getstring(32011)
        STR_BLOCKED_ITEMS = getstring(32098)
        STR_NO_BLOCKED_ITEMS = getstring(32119)
        blocked_items = self.database.get_all_blocked_itens()
        if not blocked_items:
            xbmcgui.Dialog().ok(ADDON_NAME, STR_NO_BLOCKED_ITEMS)
            return
        lines = [
            '{0} - [B]{1}[/B]'.format(x.localize_type(), x['value']) for x in blocked_items]
        lines += [STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1}'.format(ADDON_NAME, STR_BLOCKED_ITEMS), lines
        )
        if ret >= 0:
            if ret < len(blocked_items):  # managed item
                for index, item in enumerate(blocked_items):
                    if ret == index:
                        self.options(item)
                        break
            elif lines[ret] == STR_BACK:
                return

    @logged_function
    def options(self, item):
        """Provide options for a single blocked item in a dialog window."""
        STR_REMOVE = getstring(32017)
        STR_BACK = getstring(32011)
        STR_BLOCKED_ITEM_OPTIONS = getstring(32099)
        lines = [STR_REMOVE, STR_BACK]
        ret = xbmcgui.Dialog().select(
            '{0} - {1} - {2}'.format(ADDON_NAME,
                                     STR_BLOCKED_ITEM_OPTIONS, item['value']),
            lines
        )
        if ret >= 0:
            if lines[ret] == STR_REMOVE:
                self.database.delete_entrie_from_blocked(
                    item['value'],
                    item['type']
                )
                return self.view()
            elif lines[ret] == STR_BACK:
                return self.view()
        return self.view()
