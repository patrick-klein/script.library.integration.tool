#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the EpisodeItem class
'''

import os
import re
from glob import glob

import xbmc
from bs4 import BeautifulSoup

import resources.lib.database_handler  # Need to do absolute import to avoid circular import error
import resources.lib.utils as utils
from .content import ContentItem


class EpisodeItem(ContentItem):
    ''' Contains information about a TV show episode from the database,
    and has necessary functions for managing item '''

    # TODO: Use season folders in metadata/managed dir

    def __init__(self, path, title, mediatype, show_title):
        super(EpisodeItem, self).__init__(path, title, mediatype)
        self.show_title = show_title
        self._clean_show_title = None

    @property
    def clean_show_title(self):
        ''' Show title with problematic characters removed '''
        if not self._clean_show_title:
            self._clean_show_title = utils.clean_name(self.show_title)
        return self._clean_show_title

    @property
    def managed_dir(self):
        if not self._managed_dir:
            self._managed_dir = os.path.join(
                utils.MANAGED_FOLDER, 'ManagedTV', self.clean_show_title
            )
        return self._managed_dir

    @property
    def metadata_dir(self):
        if not self._metadata_dir:
            self._metadata_dir = os.path.join(utils.METADATA_FOLDER, 'TV', self.clean_show_title)
        return self._metadata_dir

    @utils.logged_function
    def add_to_library(self):
        # TODO: add a return value so Staged will know if episode wasn't added
        #       and can display a relevant notification
        # Rename episode if metadata is available
        self.rename_using_metadata()
        # Don't add episodes that don't have episode id in name
        if not re.match('.*[0-9]x[0-9].*|.*[Ss][0-9].*[Ee][0-9].*', self.clean_title):
            utils.log_msg('No episode number detected for {0}. Not adding to library...'\
                .format(self.clean_title), xbmc.LOGNOTICE)
            return
        # Check if tvshow folder already exists
        if not os.path.isdir(self.managed_dir):
            # If not, create folder in ManagedTV
            utils.fs.mkdir(self.managed_dir)
            if os.path.isdir(self.metadata_dir):
                # Link tvshow.nfo and artwork now, if self.metadata_dir exists
                files = os.listdir(self.metadata_dir)
                for fname in files:
                    if not (re.match('.*[0-9]x[0-9].*|.*[Ss][0-9].*[Ee][0-9].*', fname)
                            or '.strm' in fname):
                        utils.fs.softlink_file(
                            os.path.join(self.metadata_dir, fname),
                            os.path.join(self.managed_dir, fname)
                        )
        # Create stream file
        filepath = os.path.join(self.managed_dir, self.clean_title + '.strm')
        utils.fs.create_stream_file(self.path, filepath)
        # Link metadata for episode if it exists
        if os.path.isdir(self.metadata_dir):
            # Link nfo file for episode
            nfo_path = os.path.join(self.metadata_dir, self.clean_title + '.nfo')
            if os.path.exists(nfo_path):
                utils.fs.softlink_file(nfo_path, self.managed_dir)
            # Link thumbnail for episode
            meta_thumb_path = os.path.join(self.metadata_dir, self.clean_title + '-thumb.jpg')
            managed_thumb_path = os.path.join(self.managed_dir, self.clean_title + '-thumb.jpg')
            if os.path.exists(meta_thumb_path):
                utils.fs.softlink_file(meta_thumb_path, managed_thumb_path)
            elif utils.USE_SHOW_ARTWORK:
                # Try show landscape or fanart (since Kodi can't generate thumb for strm)
                landscape_path = os.path.join(self.metadata_dir, 'landscape.jpg')
                fanart_path = os.path.join(self.metadata_dir, 'fanart.jpg')
                if os.path.exists(landscape_path):
                    utils.fs.softlink_file(landscape_path, managed_thumb_path)
                elif os.path.exists(fanart_path):
                    utils.fs.softlink_file(fanart_path, managed_thumb_path)
        resources.lib.database_handler.DatabaseHandler().update_content(self.path, status='managed')

    @utils.logged_function
    def add_to_library_if_metadata(self):
        self.read_metadata_item()
        nfo_path = os.path.join(self.metadata_dir, self.clean_title + '.nfo')
        if os.path.exists(nfo_path):
            self.add_to_library()

    @utils.logged_function
    def create_metadata_item(self):
        # IDEA: automatically call this when staging
        # IDEA: actually create basic nfo file with name and episode number, and thumb if possible
        # IDEA: could probably just rename based on existing strm file instead of nfo file
        # Create show_dir in Metadata/TV if it doesn't already exist
        show_dir = os.path.join(utils.METADATA_FOLDER, 'TV', self.clean_show_title)
        if not os.path.exists(show_dir):
            utils.fs.mkdir(show_dir)
        # Check for existing stream file
        clean_title_no_0x0 = self.clean_title.replace('-0x0', '')
        strm_path = os.path.join(show_dir, self.clean_title + '.strm')
        # Only create metadata item if it doesn't already exist (by checking for stream title)
        if not os.path.exists(strm_path):
            # Rename file if old nfo file has episode id
            old_renamed = glob(
                os.path.join(show_dir, '*[0-9]x[0-9]* - {0}.nfo'.format(clean_title_no_0x0))
            )
            if old_renamed:
                # Prepend title with epid if so
                epid = old_renamed[0].split('/')[-1].replace(clean_title_no_0x0 + '.nfo', '')
                new_title = epid + self.title.replace('-0x0', '')
            elif not re.match('.*[0-9]x[0-9].*|.*[Ss][0-9]+[Ee][0-9].*', self.clean_title):
                # Otherwise, append -0x0 if title doesn't already have valid episode id
                new_title = self.title + '-0x0'
            else:
                new_title = self.title
            # Create a blank file so media managers can recognize it and create nfo file
            filepath = os.path.join(show_dir, utils.clean_name(new_title) + '.strm')
            utils.fs.create_empty_file(filepath)
            # Refresh item in database if name changed
            if new_title != self.title:
                self.title = new_title
                self._clean_title = utils.clean_name(new_title)
                resources.lib.database_handler.DatabaseHandler().update_content(
                    self.path, title=self.title
                )

    @utils.logged_function
    def read_metadata_item(self):
        ''' Renames the content item based on old .nfo files '''
        # TODO: resolve overlap/duplication with create_metadata_item
        # Check for existing nfo file
        show_dir = os.path.join(utils.METADATA_FOLDER, 'TV', self.clean_show_title)
        clean_title_no_0x0 = self.clean_title.replace('-0x0', '')
        if os.path.isdir(show_dir):
            # Rename item if old nfo file has episode id
            old_renamed = glob(
                os.path.join(show_dir, '*[0-9]x[0-9]* - {0}.nfo'.format(clean_title_no_0x0))
            )
            if old_renamed:
                # Prepend title with epid if so
                epid = old_renamed[0].split('/')[-1].replace(clean_title_no_0x0 + '.nfo', '')
                self.title = epid + self.title.replace('-0x0', '')
                self._clean_title = utils.clean_name(self.title)
                # Refresh item in database if name changed
                resources.lib.database_handler.DatabaseHandler().update_content(
                    self.path, title=self.title
                )

    @utils.logged_function
    def remove_and_block(self):
        # TODO: Need to remove metadata for all other items that match blocked
        dbh = resources.lib.database_handler.DatabaseHandler()
        # Add episode title to blocked
        dbh.add_blocked_item(self.title.replace('-0x0', ''), 'episode')
        # Delete metadata items
        title_path = os.path.join(
            utils.METADATA_FOLDER, 'TV', self.clean_show_title, self.clean_title
        )
        utils.fs.rm_with_wildcard(title_path)
        # Remove from db
        dbh.remove_content_item(self.path)

    @utils.logged_function
    def remove_from_library(self):
        # Delete stream & episode metadata
        utils.fs.rm_with_wildcard(os.path.join(self.managed_dir, self.clean_title))
        # Check if last stream file, and remove entire dir if so
        if os.path.isdir(self.managed_dir):
            files = os.listdir(self.managed_dir)
            for fname in files:
                if '.strm' in fname:
                    break
            else:
                utils.fs.remove_dir(self.managed_dir)

    @utils.logged_function
    def rename(self, name):
        # Rename files if they exist
        if os.path.isdir(self.metadata_dir):
            # Define "title paths" (paths without extensions)
            title_path = os.path.join(self.metadata_dir, self.clean_title)
            new_title_path = os.path.join(self.metadata_dir, utils.clean_name(name))
            # Rename stream placeholder, nfo file, and thumb
            utils.fs.mv_with_type(title_path, '.strm', new_title_path)
            utils.fs.mv_with_type(title_path, '.nfo', new_title_path)
            utils.fs.mv_with_type(title_path, '-thumb.jpg', new_title_path)
        # Rename property and refresh in staged file
        self.title = name
        self._clean_title = utils.clean_name(name)
        resources.lib.database_handler.DatabaseHandler().update_content(self.path, title=self.title)

    @utils.logged_function
    def rename_using_metadata(self):
        # TODO?: Rename show_title too
        # Read old metadata items to rename self
        self.read_metadata_item()
        # Only rename if nfo file exists
        nfo_path = os.path.join(self.metadata_dir, self.clean_title + '.nfo')
        if os.path.exists(nfo_path):
            # Open nfo file and get xml soup
            with open(nfo_path) as nfo_file:
                soup = BeautifulSoup(nfo_file, 'xml')
            # Check for season & episode tags
            season = int(soup.find('season').get_text())
            episode = int(soup.find('episode').get_text())
            # Format into episode id
            epid = '{0:02}x{1:02} - '.format(season, episode)
            # Only rename if epid not already in name (otherwise it would get duplicated)
            if epid not in self.clean_title:
                new_title = epid + self.clean_title.replace('-0x0', '')
                self.rename(new_title)
            elif '-0x0' in self.clean_title:
                new_title = self.clean_title.replace('-0x0', '')
                self.rename(new_title)
