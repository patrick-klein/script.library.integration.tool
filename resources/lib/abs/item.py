#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Defines the ABSItemShow and ABSItemMovie base class'''

import abc

class ABSItemShow(object):
    '''Abstract base class for EpisodeItem'''
    __metaclass__ = abc.ABCMeta

    def __init__(self, jsondata, year):
        self._managed_dir = None
        self._metadata_show_dir = None
        self._metadata_movie_dir = None
        self._episode_title_with_id = None


    @abc.abstractproperty
    def file(self):
        '''Create the file str'''


    @abc.abstractproperty
    def title(self):
        '''title with problematic characters removed'''


    @abc.abstractproperty
    def showtitle(self):
        '''Create the showtitle str'''


    @abc.abstractproperty
    def season(self):
        '''Create the season int'''


    @abc.abstractproperty
    def episode(self):
        '''Create the episode int'''


    @abc.abstractproperty
    def year(self):
        '''Create the year str'''


    @abc.abstractproperty
    def season_dir(self):
        '''Create the Season dir'''


    @abc.abstractproperty
    def episode_id(self):
        '''Create the ep ID'''


    @abc.abstractproperty
    def managed_show_dir(self):
        '''Path to the managed directory for the item'''


    @abc.abstractproperty
    def metadata_show_dir(self):
        '''Path to the metadata directory for the item'''


    @abc.abstractmethod
    def returasjson(self):
        '''Return all info as json'''


class ABSItemMovie(object):
    '''Abstract base class for MovieItem'''
    __metaclass__ = abc.ABCMeta

    def __init__(self, jsonitem, year):
        self._managed_dir = None
        self._metadata_movie_dir = None


    @abc.abstractproperty
    def file(self):
        '''Create the file str'''


    @abc.abstractproperty
    def title(self):
        '''Create the title str'''


    @abc.abstractproperty
    def year(self):
        '''Create the year str'''


    @abc.abstractproperty
    def managed_movie_dir(self):
        '''Path to the managed_movie_dir directory for the item'''


    @abc.abstractproperty
    def metadata_movie_dir(self):
        '''Path to the metadata directory for the item'''


    @abc.abstractmethod
    def returasjson(self):
        '''Return all info as json'''
