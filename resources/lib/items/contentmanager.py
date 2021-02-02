#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the EpisodeItem class
'''
import re
# from glob import glob
from os import listdir
from os.path import join, isdir, exists

# import xbmc
# from bs4 import BeautifulSoup

import resources.lib.database_handler  # Need to do absolute import to avoid circular import error
import resources.lib.utils as utils
from .content import ContentManager


class ContentMan(ContentManager):
    ''' Class with objectve to manager all files '''
    def __init__(self, epsodejsondata):
        super(ContentMan, self).__init__(epsodejsondata)
        # This regex has the function of detecting the patterns detected by the kodi
        # https://kodi.wiki/view/Naming_video_files/TV_shows
        self.regex_epsode_id = r'(?i)s\d{1,5}(?:(?:x|_|.)e|e)\d{1,5}|\d{1,5}x\d{1,5}'
        self.episode_title_with_id = epsodejsondata['episode_title_with_id']
        self.link_stream_path = epsodejsondata['link_stream_path']
        self.year = epsodejsondata['year']
        self.seasondir = epsodejsondata['seasondir']
        self.show_title = epsodejsondata['show_title']
        # show title + epid + eptitle
        self.formedyear = ('(%s)' % self.year)

        self.metadata_show_dir = epsodejsondata['metadata_show_dir']
        self.managed_show_dir = epsodejsondata['managed_show_dir']

        self.metadata_show_dir = ' '.join([self.metadata_show_dir, self.formedyear])
        self.managed_show_dir = ' '.join([self.managed_show_dir, self.formedyear])

        self.completeepsodetitle = ' - '.join([' '.join([self.show_title, self.formedyear]), self.episode_title_with_id])

        # managed + show dir + season dir
        self.managed_seasondir = os.path.join(self.managed_show_dir, self.seasondir)
        self.metadata_seasondir = os.path.join(self.metadata_show_dir, self.seasondir)

        # Full path of epsode without extension
        self.managed_ep_path = os.path.join(self.managed_seasondir, self.completeepsodetitle)
        self.metadata_ep_path = os.path.join(self.metadata_seasondir, self.completeepsodetitle)
        
        # Full path of muitple files with extension
        self.metadata_episode_nfo = ''.join([self.metadata_ep_path, '.nfo'])
        self.managed_episode_nfo = ''.join([self.managed_ep_path, '.nfo'])

        self.metadata_thumb_path = ''.join([self.metadata_ep_path, '-thumb.jpg'])
        self.managed_thumb_path = ''.join([self.managed_ep_path, '-thumb.jpg'])

        self.metadata_landscape_path = os.path.join(self.metadata_show_dir, 'landscape.jpg')
        self.managed_landscape_path = os.path.join(self.managed_show_dir, 'landscape.jpg')

        self.metadata_fanart_path = os.path.join(self.metadata_show_dir, 'fanart.jpg')
        self.metadata_fanart_path = os.path.join(self.managed_show_dir, 'fanart.jpg')

        self.metadata_tvshow_nfo = os.path.join(self.metadata_show_dir, 'tvshow.nfo')
        self.managed_tvshow_nfo = os.path.join(self.managed_show_dir, 'tvshow.nfo')

        self.managed_strm_path = ''.join([self.managed_ep_path, '.strm'])




    @utils.logged_function
    def add_to_library(self):
        # TODO: add a return value so Staged will know if episode wasn't added and can display a relevant notification
        # Rename episode if metadata is available
        self.rename_using_metadata()

        # create show dir 
        if not os.path.isdir(self.managed_show_dir):
            utils.fs.mkdir(self.managed_show_dir)
            pass

        # create seasondir managed season dir
        if not os.path.exists(self.managed_seasondir):
            utils.fs.mkdir(self.managed_seasondir)

        # create seasondir metadata season dir
        if not os.path.exists(self.metadata_seasondir):
            utils.fs.mkdir(self.metadata_seasondir)

        self.create_metadata_item()
        if not os.path.isdir(self.metadata_show_dir):
            utils.fs.mkdir(self.metadata_show_dir)

            # Link tvshow.nfo and artwork now, if self.metadata_show_dir exists
            for fname in os.listdir(self.metadata_show_dir):
                if not (re.match(self.regex_epsode_id, fname) or '.strm' in fname):
                    utils.fs.softlink_file(
                        os.path.join(self.metadata_show_dir, fname),
                        os.path.join(self.managed_show_dir, fname)
                    )
        try:
            # Create stream file
            utils.fs.create_stream_file(self.link_stream_path, self.managed_strm_path)
            # IDEA: Add a return true or false in create_stream_file to check if create_metadata_item will be executed
        except Exception as e:
            raise e

        # Link metadata for episode if it exists
        if os.path.isdir(self.metadata_show_dir):

            if os.path.exists(self.metadata_tvshow_nfo):
                utils.fs.softlink_file(self.metadata_tvshow_nfo, self.managed_tvshow_nfo)

            if os.path.exists(self.metadata_episode_nfo):
                utils.fs.softlink_file(self.metadata_episode_nfo, self.managed_episode_nfo)

            if os.path.exists(self.metadata_thumb_path):
                utils.fs.softlink_file(self.metadata_thumb_path, self.managed_thumb_path)

            elif utils.USE_SHOW_ARTWORK:
                # Try show landscape or fanart (since Kodi can't generate thumb for strm)

                if os.path.exists(self.metadata_landscape_path):
                    utils.fs.softlink_file(self.metadata_landscape_path, self.managed_landscape_path)

                elif os.path.exists(self.metadata_fanart_path):
                    utils.fs.softlink_file(self.metadata_fanart_path, self.metadata_fanart_path)
        
        resources.lib.database_handler.DatabaseHandler().update_content(self.link_stream_path, status='managed')


    @utils.logged_function
    def add_to_library_if_metadata(self):
        self.read_metadata_item()
        
        if os.path.exists(self.metadata_episode_nfo):
            self.add_to_library()


    @utils.logged_function
    def create_metadata_item(self):
        # IDEA: automatically call this when staging
        # IDEA: actually create basic nfo file with name and episode number, and thumb if possible
        # IDEA: could probably just rename based on existing strm file instead of nfo file
        # Create show_dir in Metadata/TV if it doesn't already exist

        if not os.path.exists(self.metadata_show_dir):
            utils.fs.mkdir(self.metadata_show_dir)

        # create a blank tvshow.nfo
        if not os.path.exists(self.metadata_tvshow_nfo):
            utils.fs.create_empty_file(self.metadata_tvshow_nfo)

        # create a blank episode nfo
        if not os.path.exists(self.metadata_episode_nfo):
            utils.fs.create_empty_file(self.metadata_episode_nfo)

        
        resources.lib.database_handler.DatabaseHandler().update_content(
            self.link_stream_path, title=self.completeepsodetitle
        )

    @utils.logged_function
    def read_metadata_item(self):
        ''' Renames the content item based on old .nfo files '''
        # TODO: resolve overlap/duplication with create_metadata_item
        # Check for existing nfo file
        # show_dir = self.managed_show_dir
        clean_title_no_0x0 = self.completeepsodetitle.replace('-0x0', '')

        if os.path.isdir(self.managed_show_dir):
            # Rename item if old nfo file has episode id
            old_renamed = glob(
                os.path.join(self.managed_show_dir, '*[0-9]+x[0-9]* - {0}.nfo'.format(clean_title_no_0x0))
            )
            if old_renamed:
                # Prepend title with epid if so
                epid = old_renamed[0].split('/')[-1].replace(clean_title_no_0x0 + '.nfo', '')
                self.title = epid + self.title.replace('-0x0', '')
                self._clean_title = utils.clean_name(self.title)
                # Refresh item in database if name changed
                resources.lib.database_handler.DatabaseHandler().update_content(
                    self.link_stream_path, title=self.title
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
        dbh.remove_content_item(self.link_stream_path)

    @utils.logged_function
    def remove_from_library(self):
        # Delete stream & episode metadata
        utils.fs.rm_with_wildcard(os.path.join(self.managed_show_dir, self.clean_title))
        # Check if last stream file, and remove entire dir if so
        if os.path.isdir(self.managed_show_dir):
            files = os.listdir(self.managed_show_dir)
            for fname in files:
                if '.strm' in fname:
                    break
            else:
                utils.fs.remove_dir(self.managed_show_dir)

    @utils.logged_function
    def rename(self, name):
        # Rename files if they exist
        if os.path.isdir(self.metadata_show_dir):
            # Define "title paths" (paths without extensions)
            title_path = os.path.join(self.metadata_show_dir, self.clean_title)
            new_title_path = os.path.join(self.metadata_show_dir, utils.clean_name(name))
            # Rename stream placeholder, nfo file, and thumb
            utils.fs.mv_with_type(title_path, '.strm', new_title_path)
            utils.fs.mv_with_type(title_path, '.nfo', new_title_path)
            utils.fs.mv_with_type(title_path, '-thumb.jpg', new_title_path)
        # Rename property and refresh in staged file
        self.title = name
        self._clean_title = utils.clean_name(name)
        resources.lib.database_handler.DatabaseHandler().update_content(self.link_stream_path, title=self.title)

    @utils.logged_function
    def rename_using_metadata(self):
        # TODO?: Rename show_title too
        # Read old metadata items to rename self
        self.read_metadata_item()
        # Only rename if nfo file exists
        nfo_path = os.path.join(self.metadata_show_dir, self.completeepsodetitle + '.nfo')
        if os.path.exists(nfo_path):
            # Open nfo file and get xml soup
            with open(nfo_path) as nfo_file:
                soup = BeautifulSoup(nfo_file)
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