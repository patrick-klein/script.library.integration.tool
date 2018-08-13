#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines BlockedItem class
'''

import resources.lib.utils as utils


class BlockedItem(dict):
    ''' Dictionary-like class that contains information about
    a blocked item in the database '''

    # TODO: Don't inherit from dict

    def __init__(self, value, blocked_type):
        super(BlockedItem, self).__init__()
        self['value'] = value
        self['type'] = blocked_type
        self._localized_type = None

    def localize_type(self):
        ''' Localize tags used for identifying mediatype '''
        if not self._localized_type:
            if self['type'] == 'movie':  # Movie
                return utils.ADDON.getLocalizedString(32102)
            elif self['type'] == 'tvshow':  # TV Show
                return utils.ADDON.getLocalizedString(32101)
            elif self['type'] == 'keyword':  # Keyword
                return utils.ADDON.getLocalizedString(32113)
            elif self['type'] == 'episode':  # Episode
                return utils.ADDON.getLocalizedString(32114)
            else:
                self._localized_type = self['type']
        return self._localized_type
