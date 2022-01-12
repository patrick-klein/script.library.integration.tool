# -*- coding: utf-8 -*-

"""Module with methos to check version."""

import sys

from os.path import isfile
from os.path import dirname

import xbmcvfs

from resources import ADDON
from resources import ADDON_ID
from resources import ADDON_VERSION

from resources.lib.filesystem import mkdir

from resources.lib.misc import getstring
from resources.lib.misc import notification


class Version():
    """Class that implements comparison operators for version numbers."""

    def __init__(self, version_number):
        """Startup version module."""
        self.version_number = version_number

    def __eq__(self, other):
        """__eq__."""
        if isinstance(other, Version):
            return self.version_number == other.version_number
        return self.version_number == other

    def __lt__(self, other):
        """__lt__."""
        if isinstance(other, Version):
            other_version = other.version_number
        else:
            other_version = other
        for this, that in zip(self.version_number.split('.'), other_version.split('.')):
            if int(this) < int(that):
                return True
            elif int(this) > int(that):
                return False
        return False

    def __ne__(self, other):
        """__ne__."""
        return not self == other

    def __gt__(self, other):
        """__gt__."""
        return not (self < other or self == other)

    def __le__(self, other):
        """__le__."""
        return self < other or self == other

    def __ge__(self, other):
        """__ge__."""
        return self > other or self == other


def check_version_file():
    """Check the version file and runs version-specific update actions."""
    # Check version file
    version_file_path = xbmcvfs.translatePath(
        f"special://userdata/addon_data/{ADDON_ID}/.version"
    )
    if isfile(version_file_path):
        with open(version_file_path, 'r') as version_file:
            version = Version(version_file.read())
    else:
        # TODO: Use the following after updating to v0.5.0
        # with open(version_file_path, 'w') as version_file:
        #     version_file.write(ADDON_VERSION)
        # version = Version(ADDON_VERSION)
        version = Version('0.3.2')
    if version != ADDON_VERSION:
        STR_UPDATING = getstring(32133)
        STR_UPDATED = getstring(32134)
        notification(message=STR_UPDATING, time=5000)
        if version < '0.4.0':
            # Maintain previous settings if managed folder is already set
            if ADDON.getSetting('managed_folder'):
                ADDON.setSetting('custom_managed_folder', 'true')
        # Create addons dir if not exist
        mkdir(dirname(version_file_path))
        # Update version file
        with open(version_file_path, 'w+') as version_file:
            version_file.write(ADDON_VERSION)
        notification(message=STR_UPDATED, time=5000)
        sys.exit()
