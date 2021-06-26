#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Defines the ContentManagerShow class'''
import re
from os import listdir
from os.path import join
from os.path import isdir
from os.path import exists
from os.path import isfile
from os.path import splitext

# from bs4 import BeautifulSoup

from resources import USE_SHOW_ARTWORK
from resources.lib.log import logged_function

from resources.lib.filesystem import mkdir
from resources.lib.filesystem import CreateNfo
from resources.lib.filesystem import remove_dir
from resources.lib.filesystem import delete_strm
from resources.lib.filesystem import softlink_file
from resources.lib.filesystem import create_stream_file
from resources.lib.filesystem import delete_with_wildcard
from resources.lib.filesystem import softlink_files_in_dir

from resources.lib.abs.content import ABSContentShow, ABSContentMovie


    '''Class with methods to manage a show item'''
    def __init__(self, database, jsondata):
        super(ContentManagerShow, self).__init__(jsondata)
        self.database = database
        # This regex has the function of detecting the patterns detected by the kodi
        # https://kodi.wiki/view/Naming_video_files/TV_shows
        self.jsondata = jsondata
        # managed + show dir + season dir
        self.metadata_season_dir = join(self.show_dir[0], self.jsondata['season_dir'])
        self.managed_season_dir = join(self.show_dir[1], self.jsondata['season_dir'])

        # Full path of episode without extension
        self.managed_ep_path = join(self.managed_season_dir, self.complete_episode_title)
        self.metadata_ep_path = join(self.metadata_season_dir, self.complete_episode_title)
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
    def complete_episode_title(self):
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


    @logged_function
    def add_to_library(self):
        # TODO: add a return value so Staged will know
        # if episode wasn't added and can display a relevant notification
        # Rename episode if metadata is available
        self.rename_using_metadata()
        # create show dir
        if not exists(self.show_dir[0]):
            try:
                mkdir(self.show_dir[0])
            except Exception as genericmkdir:
                raise genericmkdir
        if not exists(self.show_dir[1]):
            try:
                mkdir(self.show_dir[1])
            except Exception as genericmkdir:
                raise genericmkdir
        # create season_dir managed season dir
        if not exists(self.managed_season_dir):
            mkdir(self.managed_season_dir)
        # create season_dir metadata season dir
        if not exists(self.metadata_season_dir):
            mkdir(self.metadata_season_dir)
        # Create stream file
        if create_stream_file(self.link_stream_path, self.managed_strm_path):
            self.create_metadata_item()
            softlink_file(self.episode_nfo[0], self.episode_nfo[1])
            self.database.update_content(
                status='managed',
                mediatype='tvshow'
            )


    @logged_function
    def add_to_library_if_metadata(self):
        self.read_metadata_item()
        if exists(self.episode_nfo[0]):
            self.add_to_library()


    @logged_function
    def create_metadata_item(self):
        # IDEA: automatically call this when staging
        # IDEA: actually create basic nfo file with name and episode number, and thumb if possible
        # IDEA: could probably just rename based on existing strm file instead of nfo file
        # Create show_dir in Metadata/TV if it doesn't already exist
        # Create Metadate Show Dir
        if not exists(self.show_dir[0]):
            try:
                mkdir(self.show_dir[0])
            except Exception as genericmkdir:
                raise genericmkdir
        # Create Metadata Season dir
        if not exists(self.metadata_season_dir):
            mkdir(self.metadata_season_dir)
        # Create basic tvshow.nfo
        if not exists(self.metadata_tvshow_nfo):
            try:
                CreateNfo(
                    nfotype='tvshow',
                    filepath=self.metadata_tvshow_nfo,
                    jsondata=self.jsondata
                )
            except Exception:
                pass
        # Link tvshow.nfo and artwork now, if self.show_dir[0] exists
        for fname in listdir(self.show_dir[0]):
            if isfile(join(self.show_dir[0], fname)):
                if (not re.match(
                        r'(?i)s\d{1,5}(?:(?:x|_|.)e|e)\d{1,5}|\d{1,5}x\d{1,5}', fname
                    ) or '.strm' in fname):
                    if not exists(join(self.show_dir[1], fname)):
                        softlink_file(
                            join(self.show_dir[0], fname),
                            join(self.show_dir[1], fname)
                        )
        # create a basic episode nfo
        if not exists(self.episode_nfo[0]):
            try:
                CreateNfo(
                    nfotype='episodedetails',
                    filepath=self.episode_nfo[0],
                    jsondata=self.jsondata
                )
            except Exception:
                pass
        # Link metadata for episode if it exists
        if USE_SHOW_ARTWORK:
            # Try show landscape or fanart (since Kodi can't generate thumb for strm)
            if exists(self.metadata_landscape_path):
                softlink_file(
                    self.metadata_landscape_path,
                    self.managed_landscape_path
                )
            elif exists(self.metadata_fanart_path):
                softlink_file(
                    self.metadata_fanart_path,
                    self.metadata_fanart_path
                )
        self.database.update_content(
        )


    @logged_function
    def read_metadata_item(self):
        '''Renames the content item based on old .nfo files'''
        # TODO: resolve overlap/duplication with create_metadata_item
        # Check for existing nfo file
        if isdir(self.show_dir[1]):
            self.database.update_content(
            )


    @logged_function
    def remove_and_block(self):
        # TODO: Need to remove nfo for all other items that match blocked
        # Add episode title to blocked
        self.database.add_blocked_item(
        )
        # Delete nfo items
        delete_with_wildcard(splitext(self.episode_nfo[0])[0])
        # Remove from db
        self.database.remove_from(
            status=None,
            mediatype=None,
            show_title=None,
            directory=self.link_stream_path
        )


    @logged_function
    def remove_from_library(self):
        # Delete stream & episode nfo
        delete_with_wildcard(self.managed_strm_path)
        # Check if last stream file, and remove entire dir if so
        if isdir(self.show_dir[1]):
            files = listdir(self.show_dir[1])
            for fname in files:
                if '.strm' in fname:
                    break
            else:
                remove_dir(self.show_dir[1])


    # @logged_function
    # def rename(self, name):
    #     # Rename files if they exist
    #     # TODO: I supose this function is working, but not change the name,
    #     # becouse the new_title is equal the original
    #     if exists(self.show_dir[0]):
    #         # Define "title paths" (paths without extensions)
    #         title_path = join(self.show_dir[0], self.show_title)
    #         new_title_path = join(self.show_dir[0], self.show_title)
    #         # Rename stream placeholder, nfo file, and thumb
    #         mv_with_type(title_path, '.strm', new_title_path)
    #         mv_with_type(title_path, '.nfo', new_title_path)
    #         mv_with_type(title_path, '-thumb.jpg', new_title_path)
    #     # Rename property and refresh in staged file
    #     # TODO: self.show_title here is the global self.show_title
    #     # in future, the value need be updated to a new diferente formed name
    #     resources.lib.database.DatabaseHandler().update_content(
    #         self.link_stream_path,
    #         title=self.show_title,
    #         mediatype='tvshow'
    #     )



    @logged_function
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


        '''Remove the item from the database'''
        self.database.remove_from(
        '''Set the item status as staged in database'''
        self.database.update_content(
    '''Class with methods to manage a show item'''
    def __init__(self, database, jsondata):
        super(ContentManagerMovie, self).__init__(jsondata)
        self.database = database
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


    @logged_function
    def add_to_library(self):
        # create managed_movie_dir
        if not isdir(self.movie_dir[1]):
            mkdir(self.movie_dir[1])
        # Add stream file to self.managed_dir
        self.create_metadata_item()
        create_stream_file(
        self.database.update_content(
            status='managed',
            mediatype='movie'
        )


    @logged_function
    def create_metadata_item(self):
        # IDEA: automatically call this when staging
        # IDEA: could probably just rename based on existing strm file instead of nfo file
        # Create show_dir in Metadata/TV if it doesn't already exist

        if not exists(self.movie_dir[0]):
            mkdir(self.movie_dir[0])
        # create a blank movie_title.nfo
        if not exists(self.movie_nfo[0]):
            try:
                CreateNfo(
                    nfotype='movie',
                    filepath=self.movie_nfo[0],
                    jsondata=self.jsondata
                )
                softlink_files_in_dir(
                        self.movie_dir[0], self.movie_dir[1]
                    )
                delete_strm(self.movie_dir[1])
            except Exception:
                pass
        # Add metadata (optional)
        self.database.update_content(
        )


    @logged_function
    def add_to_library_if_metadata(self):
        if exists(self.movie_nfo[0]):
            self.add_to_library()


    @logged_function
    def remove_and_block(self):
        # Add title to blocked
        self.database.add_blocked_item(
            'movie'
        )
        # Delete metadata items
        remove_dir(self.movie_dir[0])
        # Remove from db
        self.database.remove_from(
            status=None,
            mediatype=None,
            show_title=None,
            directory=self.link_stream_path
        )


    @logged_function
    def remove_from_library(self):
        remove_dir(self.movie_dir[1])


    def rename(self, name):
        # TODO: Implement
        raise NotImplementedError('ContentItem.rename(name) not implemented!')


    def rename_using_metadata(self):
        # TODO: Implement
        '''Remove the item from the database'''
        self.database.remove_from(
        '''Set the item status as staged in database'''
        self.database.update_content(
