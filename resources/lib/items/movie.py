#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the MovieItem class
'''

import os.path

import resources.lib.database_handler  # Need to do absolute import to avoid circular import error
import resources.lib.utils as utils
from .content import ContentItem


class MovieItem(ContentItem):
    ''' Contains information about a TV show episode from the database,
    and has necessary functions for managing item '''

    @property
    def managed_dir(self):
        if not self._managed_dir:
            self._managed_dir = os.path.join(
                utils.MANAGED_FOLDER, 'ManagedMovies', self.clean_title
            )
        return self._managed_dir

    @property
    def metadata_dir(self):
        if not self._metadata_dir:
            self._metadata_dir = os.path.join(utils.METADATA_FOLDER, 'Movies', self.clean_title)
        return self._metadata_dir

    @utils.logged_function
    def add_to_library(self):
        # Parse and fix file/dir names
        filepath = os.path.join(self.managed_dir, self.clean_title + '.strm')
        # Create directory for movie
        utils.fs.mkdir(self.managed_dir)
        # Add metadata (optional)
        if os.path.isdir(self.metadata_dir):
            utils.fs.softlink_files_in_dir(self.metadata_dir, self.managed_dir)
            utils.fs.rm_strm_in_dir(self.managed_dir)
        # Add stream file to self.managed_dir
        utils.fs.create_stream_file(self.path, filepath)
        resources.lib.database_handler.DatabaseHandler().update_content(self.path, status='managed')

    @utils.logged_function
    def add_to_library_if_metadata(self):
        nfo_path = os.path.join(self.metadata_dir, self.clean_title + '.nfo')
        if os.path.exists(nfo_path):
            self.add_to_library()

    @utils.logged_function
    def create_metadata_item(self):
        filepath = os.path.join(self.metadata_dir, self.clean_title + '.strm')
        utils.fs.mkdir(self.metadata_dir)
        utils.fs.create_empty_file(filepath)

    @utils.logged_function
    def remove_and_block(self):
        dbh = resources.lib.database_handler.DatabaseHandler()
        # Add title to blocked
        dbh.add_blocked_item(self.title, 'movie')
        # Delete metadata items
        utils.fs.remove_dir(self.metadata_dir)
        # Remove from db
        dbh.remove_content_item(self.path)

    @utils.logged_function
    def remove_from_library(self):
        utils.fs.remove_dir(self.managed_dir)

    def rename(self, name):
        # TODO: Implement
        raise NotImplementedError('ContentItem.rename(name) not implemented!')

    def rename_using_metadata(self):
        # TODO: Implement
        raise NotImplementedError('ContentItem.rename(name) not implemented!')
