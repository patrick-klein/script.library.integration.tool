#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Defines the MovieItem class."""

from os.path import join

from resources.lib.log import logged_function
from resources.lib.abs.item import ABSItemMovie

from resources.lib.utils import MANAGED_FOLDER
from resources.lib.utils import METADATA_FOLDER


class MovieItem(ABSItemMovie):
    """Class to build information aboult movies."""

    def __init__(self, jsonitem, year=None):
        """__init__ MovieItem."""
        super(MovieItem, self).__init__(jsonitem, year)
        self._file = jsonitem['file']
        self._title = jsonitem['title']
        self._year = year if year else jsonitem['year']


    @property
    def file(self):
        """return url from strm."""
        return self._file


    @property
    def title(self):
        """return the title from content."""
        return self._title


    @property
    def year(self):
        """return the year from content."""
        return self._year


    @property
    def managed_movie_dir(self):
        """return the managed_movie_dir from content."""
        if not self._managed_dir:
            self._managed_dir = join(
                MANAGED_FOLDER, 'ManagedMovies', self.title
            )
        return self._managed_dir


    @property
    def metadata_movie_dir(self):
        """return the metadata_movie_dir from content."""
        if not self._metadata_movie_dir:
            self._metadata_movie_dir = join(METADATA_FOLDER, 'Movies', self.title)
        return self._metadata_movie_dir


    @logged_function
    def returasjson(self):
        """return the json with information from content."""
        try:
            return {
                'file': self.file,
                'title': self.title,
                'managed_movie_dir': self.managed_movie_dir,
                'metadata_movie_dir': self.metadata_movie_dir,
                'year': self.year,
                'type': 'movie'
            }
        except Exception as e:
            raise e
