# -*- coding: utf-8 -*-
# pylint: disable=broad-except

"""Defines the MovieItem class."""

import xbmc
from os.path import join

from resources.lib.log import log_msg
from resources.lib.log import logged_function

from resources.lib.manipulator import Cleaner

from resources.lib.utils import MANAGED_FOLDER


class MovieItem():
    """Class to build information aboult movies."""

    def __init__(self, jsonitem, year=None):
        """__init__ MovieItem."""
        super(__class__, self).__init__()
        self.cleaner = Cleaner()
        self.jsonitem = jsonitem
        self.arg_year = year

    def file(self):
        """Return url from strm."""
        return self.jsonitem['file']

    def title(self):
        """Return the title from content."""
        return self.cleaner.title(title=self.jsonitem['title'])

    def year(self):
        """Return the year from content."""
        return self.arg_year if self.arg_year else self.jsonitem['year']

    def managed_movie_dir(self):
        """Return the managed_movie_dir from content."""
        return join(
            MANAGED_FOLDER, 'movies', self.title()
        )

    @logged_function
    def returasjson(self):
        """Return the json with information from content."""
        try:
            return {
                'file': self.file(),
                'title': self.title(),
                'managed_movie_dir': self.managed_movie_dir(),
                'year': self.year(),
                'type': 'movie'
            }
        except Exception as error:
            log_msg('MovieItem.returasjson: %s' % error)
        return None
