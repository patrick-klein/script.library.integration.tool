#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the ContentItem base class
'''

import abc

import resources.lib.database_handler  # Need to do absolute import to avoid circular import error
import resources.lib.utils as utils


class ContentItem(object):
    ''' Abstract base class for MovieItem and EpisodeItem.
    Defines required and helper methods '''
    __metaclass__ = abc.ABCMeta

    # TODO: Make rename on add optional in settings
    # TODO: Save original_label, would be able to rename entire filename using metadata

    def __init__(self, path, title, mediatype):
        # TODO: add parent folder and optional year param
        self.path = path
        self.mediatype = mediatype
        self.title = title
        self._clean_title = None
        self._managed_dir = None
        self._metadata_dir = None

    def __str__(self):
        return '[B]{title}[/B] - [I]{path}[/I]'.format(title=self.title, path=self.path)

    @property
    def clean_title(self):
        ''' Title with problematic characters removed '''
        if not self._clean_title:
            self._clean_title = utils.clean_name(self.title)
        return self._clean_title

    @abc.abstractproperty
    def managed_dir(self):
        ''' Path to the managed directory for the item '''

    @abc.abstractproperty
    def metadata_dir(self):
        ''' Path to the metadata directory for the item '''

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
        resources.lib.database_handler.DatabaseHandler().remove_content_item(self.path)

    def set_as_staged(self):
        ''' Set the item status as staged in database '''
        resources.lib.database_handler.DatabaseHandler().update_content(self.path, status='staged')
