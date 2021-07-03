#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines the SyncedItem class."""

from resources.lib.utils import getlocalizedstring


class SyncedItem(dict):
    """Dictionary-like class that contains information about a synced directory in the database."""

    def __init__(self, directory, label, synced_type):
        """SyncedItem __init__."""
        super(SyncedItem, self).__init__()
        self['file'] = directory
        self['label'] = label
        self['type'] = synced_type
        self._localized_type = None

    def localize_type(self):
        """Localize tags used for identifying type."""
        _TYPES = {
            'movie': 32109,
            'tvshow': 32108,
            'single-movie': 32116,
            'single-tvshow': 32115
        }
        self._localized_type = getlocalizedstring(_TYPES[self['type']])
        return self._localized_type
