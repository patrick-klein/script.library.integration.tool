# -*- coding: utf-8 -*-

"""Defines BlockedItem class."""

from resources.lib.misc import getstring


class BlockedItem(dict):
    """Dictionary-like class that contains information about a blocked item in the database."""

    # TODO: Don't inherit from dict

    def __init__(self, value, blocked_type):
        """__init__ BlockedItem."""
        super(__class__, self).__init__()
        self['value'] = value
        self['type'] = blocked_type
        self._localized_type = None

    def localize_type(self):
        """Localize tags used for identifying type."""
        _TYPES = {
            'movie': 32102,
            'tvshow': 32101,
            'keyword': 32113,
            'episode': 32114
        }
        if not self._localized_type:
            try:
                return getstring(_TYPES[self['type']])
            except KeyError:
                self._localized_type = self['type']
        return self._localized_type
