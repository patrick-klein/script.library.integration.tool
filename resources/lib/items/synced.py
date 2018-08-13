#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the SyncedItem class
'''

import resources.lib.utils as utils


class SyncedItem(dict):
    ''' Dictionary-like class that contains information about
    a synced directory in the database '''

    def __init__(self, directory, label, synced_type):
        super(SyncedItem, self).__init__()
        self['dir'] = directory
        self['label'] = label
        self['type'] = synced_type
        self._localized_type = None

    def localize_type(self):
        ''' Localizes tags used for identifying mediatype '''
        if not self._localized_type:
            if self['type'] == 'movie':  # Movies
                self._localized_type = utils.ADDON.getLocalizedString(32109)
            elif self['type'] == 'tvshow':  # TV Shows
                self._localized_type = utils.ADDON.getLocalizedString(32108)
            elif self['type'] == 'single-movie':  # Single Movie
                self._localized_type = utils.ADDON.getLocalizedString(32116)
            elif self['type'] == 'single-tvshow':  # Single TV Show
                self._localized_type = utils.ADDON.getLocalizedString(32115)
            else:
                self._localized_type = self['type']
        return self._localized_type
