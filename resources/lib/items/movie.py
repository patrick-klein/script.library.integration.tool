#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the MovieItem class
'''

from os.path import join, isdir

from resources.lib.abs.item import ABSItemMovie



class MovieItem(ABSItemMovie):
    ''' Contains information about a TV show episode from the database,
    and has necessary functions for managing item '''
    def __init__(self, link_stream_path, title, mediatype, year=None):
        super(MovieItem, self).__init__(link_stream_path, title, mediatype, year)
        self._link_stream_path = link_stream_path
        self._movie_title = title
        self._year = year

    @property
    def link_stream_path(self):
        return self._link_stream_path

    @property
    def movie_title(self):
        return self._movie_title

    @property
    def year(self):
        ''' Show title with problematic characters removed '''
        return self._year    

    @property
    def managed_movie_dir(self):
        if not self._managed_dir:
            self._managed_dir = join(
                utils.MANAGED_FOLDER, 'ManagedMovies', self.movie_title
            )
        return self._managed_dir

    @property
    def metadata_movie_dir(self):
        if not self._metadata_movie_dir:
            self._metadata_movie_dir = join(utils.METADATA_FOLDER, 'Movies', self.movie_title)
        return self._metadata_movie_dir

    @utils.logged_function
    def returasjson(self):
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