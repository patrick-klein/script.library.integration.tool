# -*- coding: utf-8 -*-
# pylint: disable=broad-except

"""Defines the MovieItem class."""

from os.path import join

from resources.lib.log import logged_function
from resources.lib.abs.item import ABSItemMovie

from resources.lib.manipulator import Cleaner
from resources.lib.utils import MANAGED_FOLDER


class MovieItem():
    """Class to build information aboult movies."""

    def __init__(self, jsonitem, year=None):
        """__init__ MovieItem."""
        super(MovieItem, self).__init__(jsonitem, year)
        self.cleaner = Cleaner()
        self._file = jsonitem['file']
        self._title = self.cleaner.title(title=jsonitem['title'])
        self._year = year if year else jsonitem['year']

    @property
    def file(self):
        """Return url from strm."""
        return self._file

    @property
    def title(self):
        """Return the title from content."""
        return self._title

    @property
    def year(self):
        """Return the year from content."""
        return self._year

    @property
    def managed_movie_dir(self):
        """Return the managed_movie_dir from content."""
        if not self._managed_dir:
            self._managed_dir = join(
                MANAGED_FOLDER, 'movies', self.title
            )
        return self._managed_dir

    @logged_function
    def returasjson(self):
        """Return the json with information from content."""
        try:
            return {
                'file': self.file,
                'title': self.title,
                'managed_movie_dir': self.managed_movie_dir,
                'year': self.year,
                'type': 'movie'
            }
        except Exception as e:
            raise e
