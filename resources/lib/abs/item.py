#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the ABSItemShow and ABSItemMovie base class
'''

import abc

class ABSItemShow(object):
    ''' Abstract base class for MovieItem and EpisodeItem.
    Defines required and helper methods '''
    __metaclass__ = abc.ABCMeta
    def __init__(self, link_stream_path, title, mediatype, show_title=None, season=None, epnumber=None, year=None):
        self._managed_dir = None
        self._metadata_show_dir = None
        self._metadata_movie_dir = None
        self._episode_title_with_id = None


    @abc.abstractproperty
    def link_stream_path(self):
        ''' Create the link_stream_path str'''


    @abc.abstractproperty
    def episode_title(self):
        ''' episode_title with problematic characters removed '''


    @abc.abstractproperty
    def show_title(self):
        ''' Create the show_title str '''


    @abc.abstractproperty
    def season_number(self):
        ''' Create the season_number int '''


    @abc.abstractproperty
    def episode_number(self):
        ''' Create the episode_number int '''


    @abc.abstractproperty
    def year(self):
        ''' Create the year str '''


    @abc.abstractproperty
    def season_dir(self):
        ''' Create the Season dir '''


    @abc.abstractproperty
    def episode_id(self):
        ''' Create the ep ID '''


    @abc.abstractproperty
    def managed_show_dir(self):
        ''' Path to the managed directory for the item '''


    @abc.abstractproperty
    def metadata_show_dir(self):
        ''' Path to the metadata directory for the item '''


    @abc.abstractmethod
    def returasjson(self):
        ''' Return all info as json '''


class ABSItemMovie(object):
    ''' Abstract base class for MovieItem and EpisodeItem.
    Defines required and helper methods '''
    __metaclass__ = abc.ABCMeta
    def __init__(self, link_stream_path, title, mediatype, year=None):
        self._managed_dir = None
        self._metadata_movie_dir = None


    @abc.abstractproperty
    def link_stream_path(self):
        ''' Create the link_stream_path str'''


    @abc.abstractproperty
    def movie_title(self):
        ''' Create the link_stream_path str'''


    @abc.abstractproperty
    def year(self):
        ''' Create the year str '''


    @abc.abstractproperty
    def managed_movie_dir(self):
        ''' Path to the managed_movie_dir directory for the item '''


    @abc.abstractproperty
    def metadata_movie_dir(self):
        ''' Path to the metadata directory for the item '''


    @abc.abstractmethod
    def returasjson(self):
        ''' Return all info as json '''
