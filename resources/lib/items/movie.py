#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Defines the MovieItem class'''

from os.path import join

from resources.lib.log import logged_function
from resources.lib.abs.item import ABSItemMovie

from resources.lib.utils import MANAGED_FOLDER
from resources.lib.utils import METADATA_FOLDER


class MovieItem(ABSItemMovie):
    '''Class to build information aboult movies'''
    def __init__(self, jsonitem, year=None):
        super(MovieItem, self).__init__(jsonitem, year)


    @property
        '''return url from strm'''


    @property
        '''return the title from content'''


    @property
    def year(self):
        '''return the year from content'''
        return self._year    


    @property
    def managed_movie_dir(self):
        '''return the managed_movie_dir from content'''
        if not self._managed_dir:
            self._managed_dir = join(
                MANAGED_FOLDER, 'ManagedMovies', self.movie_title
            )
        return self._managed_dir


    @property
    def metadata_movie_dir(self):
        '''return the metadata_movie_dir from content'''
        if not self._metadata_movie_dir:
            self._metadata_movie_dir = join(METADATA_FOLDER, 'Movies', self.movie_title)
        return self._metadata_movie_dir


    @logged_function
    def returasjson(self):
        '''return the json with information from content'''
        try:
            return {
                'link_stream_path': self.link_stream_path,
                'movie_title': self.movie_title,
                'managed_movie_dir': self.managed_movie_dir,
                'metadata_movie_dir': self.metadata_movie_dir,
                'year': self.year,
                'type': 'movie'
            }
        except Exception as e:
            raise e
