#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the EpisodeItem class
'''
import re
from os import listdir
from os.path import join, isdir, exists, splitext, isfile

from bs4 import BeautifulSoup

import resources.lib.database_handler  # Need to do absolute import to avoid circular import error
import resources.lib.utils as utils
from .content import ContentManagerShows, ContentManagerMovies


class ContentManShows(ContentManagerShows):
    ''' Class with objectve to manager all files '''
    def __init__(self, jsondata):
        super(ContentManShows, self).__init__(jsondata)
        # This regex has the function of detecting the patterns detected by the kodi
        # https://kodi.wiki/view/Naming_video_files/TV_shows
        self.jsondata = jsondata
        utils.tojs(jsondata, 'jsondata')
        # managed + show dir + season dir
        self.metadata_seasondir = join(self.show_dir[0], self.jsondata['seasondir'])
        self.managed_seasondir = join(self.show_dir[1], self.jsondata['seasondir'])

        # Full path of epsode without extension
        self.managed_ep_path = join(self.managed_seasondir, self.complete_epsode_title)
        self.metadata_ep_path = join(self.metadata_seasondir, self.complete_epsode_title)
        # Full path of muitple files with extension

        self.metadata_thumb_path = ''.join([self.metadata_ep_path, '-thumb.jpg'])
        self.managed_thumb_path = ''.join([self.managed_ep_path, '-thumb.jpg'])

        self.metadata_landscape_path = join(self.show_dir[0], 'landscape.jpg')
        self.managed_landscape_path = join(self.show_dir[1], 'landscape.jpg')

        self.metadata_fanart_path = join(self.show_dir[0], 'fanart.jpg')
        self.metadata_fanart_path = join(self.show_dir[1], 'fanart.jpg')

        self.metadata_tvshow_nfo = join(self.show_dir[0], 'tvshow.nfo')
        self.managed_tvshow_nfo = join(self.show_dir[1], 'tvshow.nfo')

        self.managed_strm_path = ''.join([self.managed_ep_path, '.strm'])

    @property
    def show_title(self):
        return self.jsondata['show_title']

    @property
    def show_dir(self):
        return (
            ' '.join([self.jsondata['metadata_show_dir'], self.formedyear]),
            ' '.join([self.jsondata['managed_show_dir'], self.formedyear])
        )

    @property
    def formedyear(self):
        return '(%s)' % self.jsondata['year']

    @property
    def complete_epsode_title(self):
        return '%s - %s' % (
            ' '.join([self.show_title, self.formedyear]),
            self.episode_title_with_id
        )

    @property
    def link_stream_path(self):
        return self.jsondata['link_stream_path']

    @property
    def episode_title_with_id(self):
        return self.jsondata['episode_title_with_id']

    @property
    def episode_nfo(self):
        return (
            ''.join([self.metadata_ep_path, '.nfo']), ''.join([self.managed_ep_path, '.nfo'])
        )

    @utils.logged_function
    def add_to_library(self):
        # TODO: add a return value so Staged will know
        # if episode wasn't added and can display a relevant notification
        # Rename episode if metadata is available
        self.rename_using_metadata()

        # create show dir
        if not exists(self.show_dir[0]):
            try:
                utils.fs.mkdir(self.show_dir[0])
            except Exception as e:
                raise e

        if not exists(self.show_dir[1]):
            try:
                utils.fs.mkdir(self.show_dir[1])
            except Exception as e:
                raise e

        # create seasondir managed season dir
        if not exists(self.managed_seasondir):
            utils.fs.mkdir(self.managed_seasondir)

        # create seasondir metadata season dir
        if not exists(self.metadata_seasondir):
            utils.fs.mkdir(self.metadata_seasondir)

        # Create stream file
        if utils.fs.create_stream_file(self.link_stream_path, self.managed_strm_path):            
            self.create_metadata_item()
            utils.fs.softlink_file(self.episode_nfo[0], self.episode_nfo[1])
            resources.lib.database_handler.DatabaseHandler().update_content(
                self.link_stream_path,
                status='managed',
                mediatype='tvshow'
            )

    @utils.logged_function
    def add_to_library_if_metadata(self):
        self.read_metadata_item()
        if exists(self.episode_nfo[0]):
            self.add_to_library()


    @utils.logged_function
    def create_metadata_item(self):
        # IDEA: automatically call this when staging
        # IDEA: actually create basic nfo file with name and episode number, and thumb if possible
        # IDEA: could probably just rename based on existing strm file instead of nfo file
        # Create show_dir in Metadata/TV if it doesn't already exist

        # Create Metadate Show Dir
        if not exists(self.show_dir[0]):
            try:
                utils.fs.mkdir(self.show_dir[0])
            except Exception as e:
                raise 

        # Create Metadata Season dir
        if not exists(self.metadata_seasondir):
            utils.fs.mkdir(self.metadata_seasondir)

        # Create basic tvshow.nfo
        if not exists(self.metadata_tvshow_nfo):
            try:
                utils.fs.CreateNfo(
                    nfotype='tvshow',
                    filepath=self.metadata_tvshow_nfo,
                    jsondata=self.jsondata
                )
            except Exception as e:
                raise e
        # Link tvshow.nfo and artwork now, if self.show_dir[0] exists
        for fname in listdir(self.show_dir[0]):
            if isfile(join(self.show_dir[0], fname)):
                if (not re.match(r'(?i)s\d{1,5}(?:(?:x|_|.)e|e)\d{1,5}|\d{1,5}x\d{1,5}', fname)
                or '.strm' in fname):
                    if not exists(join(self.show_dir[1], fname)):
                        utils.fs.softlink_file(
                            join(self.show_dir[0], fname),
                            join(self.show_dir[1], fname)
                        )

        # create a basic episode nfo
        if not exists(self.episode_nfo[0]):
            try:
                utils.fs.CreateNfo(
                    nfotype='episodedetails',
                    filepath=self.episode_nfo[0],
                    jsondata=self.jsondata
                )
            except Exception as e:
                raise e
        # # Link metadata for episode if it exists
        # if utils.USE_SHOW_ARTWORK:
        #     # Try show landscape or fanart (since Kodi can't generate thumb for strm)
        #     if exists(self.metadata_landscape_path):
        #         utils.fs.softlink_file(
        #             self.metadata_landscape_path,
        #             self.managed_landscape_path
        #         )
        #     elif exists(self.metadata_fanart_path):
        #         utils.fs.softlink_file(
        #             self.metadata_fanart_path,
        #             self.metadata_fanart_path
        #         )

 

        resources.lib.database_handler.DatabaseHandler().update_content(
            self.link_stream_path, 
            title=self.jsondata['episode_title'], 
            mediatype='tvshow'
        )


    @utils.logged_function
    def read_metadata_item(self):
        ''' Renames the content item based on old .nfo files '''
        # TODO: resolve overlap/duplication with create_metadata_item
        # Check for existing nfo file
        if isdir(self.show_dir[1]):
            resources.lib.database_handler.DatabaseHandler().update_content(
                self.link_stream_path,
                title=self.jsondata['episode_title'],
                mediatype='tvshow'
            )

    @utils.logged_function
    def remove_and_block(self):
        # TODO: Need to remove metadata for all other items that match blocked
        dbh = resources.lib.database_handler.DatabaseHandler()
        # Add episode title to blocked
        dbh.add_blocked_item(self.show_title, 'episode')
        # Delete metadata items
        # title_path = join(
        #     utils.METADATA_FOLDER, 'TV', self.clean_show_title, self.clean_title
        # )
        utils.fs.rm_with_wildcard(splitext(self.episode_nfo[0])[0])
        # Remove from db
        # TODO: FIX pass mediatype to this func
        dbh.DatabaseHandler().remove_from(
            status=None,
            mediatype=None,
            show_title=None,
            directory=self.link_stream_path
            )

    @utils.logged_function
    def remove_from_library(self):
        # Delete stream & episode metadata
        utils.fs.rm_with_wildcard(self.managed_strm_path)
        # Check if last stream file, and remove entire dir if so
        if isdir(self.show_dir[1]):
            files = listdir(self.show_dir[1])
            for fname in files:
                if '.strm' in fname:
                    break
            else:
                utils.fs.remove_dir(self.show_dir[1])

    @utils.logged_function
    def rename(self, name):
        # Rename files if they exist

        # TODO: I supose this function is working, but not chante the name, 
        # becouse the new_title is equal the original
        if exists(self.show_dir[0]):
            # Define "title paths" (paths without extensions)
            title_path = join(self.show_dir[0], self.show_title)
            new_title_path = join(self.show_dir[0], self.show_title)
            # Rename stream placeholder, nfo file, and thumb
            utils.fs.mv_with_type(title_path, '.strm', new_title_path)
            utils.fs.mv_with_type(title_path, '.nfo', new_title_path)
            utils.fs.mv_with_type(title_path, '-thumb.jpg', new_title_path)

        # Rename property and refresh in staged file
        # TODO: self.show_title here is the global self.show_title
        # in future, the value need be updated to a new diferente formed name
        resources.lib.database_handler.DatabaseHandler().update_content(
            self.link_stream_path,
            title=self.show_title,
            mediatype='tvshow'
        )

    @utils.logged_function
    def rename_using_metadata(self):
        # TODO?: Rename show_title too
        # Read old metadata items to rename self
        self.read_metadata_item()

        # # Only rename if nfo file exists
        # if exists(self.episode_nfo[0]):
        #     # Open nfo file and get xml soup
        #     with open(self.episode_nfo[0]) as nfo_file:
        #         soup = BeautifulSoup(nfo_file)
        #     # Check for season & episode tags
        #     season = int(soup.find('season').get_text())
        #     episode = int(soup.find('episode').get_text())
        #     # Format into episode id
        #     epid = '{0:02}x{1:02} - '.format(season, episode)
        #     # Only rename if epid not already in name (otherwise it would get duplicated)
        #     if epid not in self.clean_title:
        #         new_title = epid + self.clean_title.replace('-0x0', '')
        #         self.rename(new_title)
        #     elif '-0x0' in self.clean_title:
        #         new_title = self.clean_title.replace('-0x0', '')
        #         self.rename(new_title)


class ContentManMovies(ContentManagerMovies):
    ''' Contains information about a TV show episode from the database,
    and has necessary functions for managing item '''
    def __init__(self, jsondata):
        super(ContentManMovies, self).__init__(jsondata)
        self.jsondata = jsondata

        self.managed_strm_path = join(
                self.movie_dir[1], ''.join([self.movie_title, '.strm'])
            )

    @property
    def link_stream_path(self):
        return self.jsondata['link_stream_path']

    @property
    def movie_title(self):
        return ' '.join([self.jsondata['movie_title'], self.formedyear])

    @property
    def year(self):
        return self.jsondata['year']

    @property
    def formedyear(self):
        return '(%s)' % self.jsondata['year']

    @property
    def movie_dir(self):
        return (
            ' '.join([self.jsondata['metadata_movie_dir'], self.formedyear]),
            ' '.join([self.jsondata['managed_movie_dir'], self.formedyear])
        )

    @property
    def movie_nfo(self):
        return (
            join(self.movie_dir[0], ''.join([self.movie_title, '.nfo'])),
            join(self.movie_dir[1], ''.join([self.movie_title, '.nfo']))
        )


    @utils.logged_function
    def add_to_library(self):
        # create managed_movie_dir
        if not isdir(self.movie_dir[1]):
            utils.fs.mkdir(self.movie_dir[1])

        # Add stream file to self.managed_dir
        self.create_metadata_item()

        utils.fs.create_stream_file(
            self.link_stream_path, self.managed_strm_path)
        resources.lib.database_handler.DatabaseHandler().update_content(
                self.link_stream_path,
                status='managed',
                mediatype='movie'
            )

    @utils.logged_function
    def create_metadata_item(self):
        # IDEA: automatically call this when staging
        # IDEA: actually create basic nfo file with name and episode number, and thumb if possible
        # IDEA: could probably just rename based on existing strm file instead of nfo file
        # Create show_dir in Metadata/TV if it doesn't already exist

        if not exists(self.movie_dir[0]):
            utils.fs.mkdir(self.movie_dir[0])
        # create a blank movie_title.nfo
        if not exists(self.movie_nfo[0]):
            try:
                utils.fs.CreateNfo(
                    nfotype='movie',
                    filepath=self.movie_nfo[0],
                    jsondata=self.jsondata
                )
                utils.fs.softlink_files_in_dir(
                        self.movie_dir[0], self.movie_dir[1]
                    )
                # utils.fs.rm_strm_in_dir(self.movie_dir[1])
            except Exception as e:
                raise e
        # Add metadata (optional)
        resources.lib.database_handler.DatabaseHandler().update_content(
                self.link_stream_path,
                title=self.jsondata['movie_title'],
                mediatype='movie'
            )

    @utils.logged_function
    def add_to_library_if_metadata(self):
        if exists(self.movie_nfo[0]):
            self.add_to_library()


    @utils.logged_function
    def remove_and_block(self):
        dbh = resources.lib.database_handler.DatabaseHandler()
        # Add title to blocked
        dbh.add_blocked_item(self.movie_title, 'movie')
        # Delete metadata items
        utils.fs.remove_dir(self.movie_dir[0])
        # Remove from db
        # TODO: FIX pass mediatype to this func
        dbh.DatabaseHandler().remove_from(
            status=None,
            mediatype=None,
            show_title=None,
            directory=self.link_stream_path
            )
            
    @utils.logged_function
    def remove_from_library(self):
        utils.fs.remove_dir(self.movie_dir[1])

    def rename(self, name):
        # TODO: Implement
        raise NotImplementedError('ContentItem.rename(name) not implemented!')

    def rename_using_metadata(self):
        # TODO: Implement
        raise NotImplementedError('ContentItem.rename(name) not implemented!')
