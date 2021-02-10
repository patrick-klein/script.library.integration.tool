#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the ContentItemShow and ContentItemMovies base class
'''

import abc

import resources.lib.database_handler  # Need to do absolute import to avoid circular import error
import resources.lib.utils as utils

class ContentItemShow(object):
    ''' Abstract base class for MovieItem and EpisodeItem.
    Defines required and helper methods '''
    __metaclass__ = abc.ABCMeta

    def __init__(self, link_stream_path, title, mediatype, show_title=None, season=None, epnumber=None, year=None):
        self._managed_dir = None
        self.movie_title = None
        self._metadata_show_dir = None
        self._metadata_movie_dir = None
    # 
    @abc.abstractproperty
    def link_stream_path(self):
        ''' Create the link_stream_path str'''

    @abc.abstractproperty
    def epsode_title(self):
        ''' epsode_title with problematic characters removed '''

    @abc.abstractproperty
    def show_title(self):
        ''' Create the show_title str '''

    @abc.abstractproperty
    def season_number(self):
        ''' Create the season_number int '''

    @abc.abstractproperty
    def epsode_number(self):
        ''' Create the epsode_number int '''

    @abc.abstractproperty
    def year(self):
        ''' Create the year str '''
    # 
    # # 
    @abc.abstractproperty
    def seasondir(self):
        ''' Create the Season dir '''

    @abc.abstractproperty
    def epsodeid(self):
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

class ContentItemMovies(object):
    ''' Abstract base class for MovieItem and EpisodeItem.
    Defines required and helper methods '''
    __metaclass__ = abc.ABCMeta

    def __init__(self, link_stream_path, title, mediatype, year=None):
        self._managed_dir = None
        self._metadata_movie_dir = None
    # 
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


class ContentManagerShows(object):
    ''' Abstract base class for ContentManager.
    Defines required and helper methods '''
    __metaclass__ = abc.ABCMeta

    # TODO: Make rename on add optional in settings
    # TODO: Save original_label, would be able to rename entire filename using metadata

    def __init__(self, jsondata):
        self._link_stream_path = None
        self._episode_title = None
        # mediatype
        self._show_title = None
        self._season = None
        self._epsode_number = None
        self._year = None

    def __str__(self):
        return '[B]{title}[/B] - [I]{path}[/I]'.format(title=self.episode_title_with_id, path=self.link_stream_path)

    @abc.abstractproperty
    def show_title(self):
        ''' Path to the show_dir directory for the item '''

    @abc.abstractproperty
    def show_dir(self):
        ''' Path to the show_dir directory for the item '''

    @abc.abstractproperty
    def formedyear(self):
        ''' Path to the formedyear directory for the item '''

    @abc.abstractproperty
    def complete_epsode_title(self):
        ''' Path to the complete_epsode_title directory for the item '''

    @abc.abstractproperty
    def link_stream_path(self):
        ''' Path to the episode_title_with_id directory for the item '''
    
    @abc.abstractproperty
    def episode_title_with_id(self):
        ''' Path to the episode_title_with_id directory for the item '''

    @abc.abstractproperty
    def episode_nfo(self):
        ''' Path to the episode_nfo directory for the item '''
        
    @abc.abstractmethod
    def add_to_library(self):
        ''' Add content to the library '''
        # TODO: add to library using json-rpc

    @abc.abstractmethod
    def add_to_library_if_metadata(self):
        ''' Add content to the library only if it has metadata '''

    @abc.abstractmethod
    def remove_from_library(self):
        ''' Remove its content from the library, does NOT change/remove item in database '''
        # TODO: remove from library using json-rpc

    @abc.abstractmethod
    def remove_and_block(self):
        ''' Remove content from the library, deletes metadata, and adds to blocked list '''

    @abc.abstractmethod
    def create_metadata_item(self):
        ''' Add relevent files to metadata folder '''

    @abc.abstractmethod
    def rename_using_metadata(self):
        ''' Automatically rename using nfo file '''

    @abc.abstractmethod
    def rename(self, name):
        ''' Rename title and files '''

    def delete(self):
        ''' Remove the item from the database '''
        resources.lib.database_handler.DatabaseHandler().remove_from(
            status=None,
            mediatype=None,
            show_title=None,
            directory=self.link_stream_path
            )

    def set_as_staged(self):
        ''' Set the item status as staged in database '''
        resources.lib.database_handler.DatabaseHandler().update_content(
                self.link_stream_path,
                status='staged',
                mediatype='tvshow'
            )
# # # #
# # # #
# # # #
class ContentManagerMovies(object):
    ''' Abstract base class for ContentManager.
    Defines required and helper methods '''
    __metaclass__ = abc.ABCMeta

    # TODO: Make rename on add optional in settings
    # TODO: Save original_label, would be able to rename entire filename using metadata

    def __init__(self, jsondata):
        self._link_stream_path = None
        # mediatype
        self._movie_title = None
        self._year = None

    def __str__(self):
        return '[B]{title}[/B] - [I]{path}[/I]'.format(title=self.movie_title, path=self.link_stream_path)

    @abc.abstractproperty
    def link_stream_path(self):
        ''' Path to the episode_title_with_id directory for the item '''

    @abc.abstractproperty
    def movie_title(self):
        ''' Path to the show_dir directory for the item '''

    @abc.abstractproperty
    def year(self):
        ''' Path to the year for the item '''

    @abc.abstractproperty
    def formedyear(self):
        ''' Path to the formedyear for the item '''

    @abc.abstractproperty
    def movie_dir(self):
        ''' Path to the movie_nfo for the item '''

    @abc.abstractproperty
    def movie_nfo(self):
        ''' Path to the movie_nfo for the item '''

    # @abc.abstractproperty
    # def show_dir(self):
    #     ''' Path to the show_dir directory for the item '''

    # @abc.abstractproperty
    # def formedyear(self):
    #     ''' Path to the formedyear directory for the item '''

    # @abc.abstractproperty
    # def complete_epsode_title(self):
    #     ''' Path to the complete_epsode_title directory for the item '''

    # @abc.abstractproperty
    # def episode_nfo(self):
    #     ''' Path to the episode_nfo directory for the item '''
        
    @abc.abstractmethod
    def add_to_library(self):
        ''' Add content to the library '''
        # TODO: add to library using json-rpc

    @abc.abstractmethod
    def add_to_library_if_metadata(self):
        ''' Add content to the library only if it has metadata '''

    @abc.abstractmethod
    def remove_from_library(self):
        ''' Remove its content from the library, does NOT change/remove item in database '''
        # TODO: remove from library using json-rpc

    @abc.abstractmethod
    def remove_and_block(self):
        ''' Remove content from the library, deletes metadata, and adds to blocked list '''

    @abc.abstractmethod
    def create_metadata_item(self):
        ''' Add relevent files to metadata folder '''

    @abc.abstractmethod
    def rename_using_metadata(self):
        ''' Automatically rename using nfo file '''

    @abc.abstractmethod
    def rename(self, name):
        ''' Rename title and files '''

    def delete(self):
        ''' Remove the item from the database '''
        resources.lib.database_handler.DatabaseHandler().remove_from(
            status=None,
            mediatype=None,
            show_title=None,
            directory=self.link_stream_path
            )

    def set_as_staged(self):
        ''' Set the item status as staged in database '''
        resources.lib.database_handler.DatabaseHandler().update_content(
            self.link_stream_path,
            status='staged',
            mediatype='tvshow'            
        )