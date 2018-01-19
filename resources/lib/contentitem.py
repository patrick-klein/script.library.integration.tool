#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import cPickle as pickle
import xbmc

from bs4 import BeautifulSoup

from fnmatch import fnmatch
from glob import glob


from utils import log_msg, get_items, save_items, clean

managed_folder = '/Volumes/Drobo Media/LibraryTools/'

class ContentItem(object):
    #?TODO: remove mediatype from init now that there are subclasses
    #TODO: create refresh method so you don't have to remove_from_staged then add_to_staged_file
    #TODO: make rename on add & metadata on stage optional in settings
    #TODO: save original_label, would be able to rename entire filename using metadata

    def __init__(self, path, title, mediatype):
        #TODO: add parent folder and optional year param
        #TODO: move create_metadata_item to new stage() method
        self.path = path.encode('utf-8')
        self.title = title.encode('utf-8')
        self.mediatype = mediatype.encode('utf-8')

    def __str__(self):
        return '[B]%s[/B] - [I]%s[/I]' % (self.title, self.path)

    def add_to_library(self):
        #TODO: add to library using json-rpc
        raise NotImplementedError('ContentItem.add_to_library() not implemented!')

    def remove_from_library(self):
        #TODO: remove from library using json-rpc
        raise NotImplementedError('ContentItem.remove_from_library() not implemented!')

    def create_metadata_item(self):
        # TODO maybe: create subfolders in metadata_dir named after plugins
        #   put the movie and tv folders in there
        #   it would make it easier to share, but tougher for scraping
        raise NotImplementedError('ContentItem.create_metadata_item() not implemented!')

    def rename_using_metadata(self):
        raise NotImplementedError('ContentItem.rename_using_metadata() not implemented!')

    def rename(self, name):
        raise NotImplementedError('ContentItem.rename_using_metadata(name) not implemented!')

    def add_to_managed_file(self):
        items = get_items('managed.pkl')
        items.append(self)
        save_items('managed.pkl', items)

    def add_to_staged_file(self):
        # TODO: create stage() method, and move the call to create_metadata_item there
        items = get_items('staged.pkl')
        items.append(self)
        save_items('staged.pkl', items)

    def remove_from_managed(self):
        managed = get_items('managed.pkl')
        for item in managed:
            if item.get_path()==self.path:
                managed.remove(item)
        save_items('managed.pkl',managed)

    def remove_from_staged(self):
        staged = get_items('staged.pkl')
        for item in staged:
            if item.get_path()==self.path:
                staged.remove(item)
        save_items('staged.pkl',staged)

    def get_title(self):
        return self.title

    def get_path(self):
        return self.path

    def get_mediatype(self):
        return self.mediatype

class MovieItem(ContentItem):

    def __init__(self, path, title, mediatype):
        super(MovieItem, self).__init__(path, title, mediatype)

    def add_to_library(self):
        # parse and fix file/dir names
        safe_title = clean(self.title)
        movie_dir = os.path.join(managed_folder, 'ManagedMovies', safe_title)
        filepath = os.path.join(movie_dir, safe_title + '.strm')
        # create directory for movie
        os.system('mkdir "%s"' % movie_dir)
        # add metadata (optional)
        metadata_dir = os.path.join(managed_folder, 'Metadata', 'Movies', safe_title)
        if os.path.isdir(metadata_dir):
            os.system('ln -s "%s/"* "%s"' % (metadata_dir, movie_dir))
            os.system('rm "%s/*.strm"' % movie_dir)
        # add stream file to movie_dir
        os.system('echo "%s" > "%s"' % (self.path, filepath) )
        # add to managed file
        self.add_to_managed_file()
        self.remove_from_staged()

    def remove_from_library(self):
        safe_title = clean(self.title)
        movie_dir = os.path.join(managed_folder, 'ManagedMovies', safe_title)
        os.system('rm -r "%s"' % movie_dir)
        self.remove_from_managed()

    def create_metadata_item(self):
        safe_title = clean(self.title)
        movie_dir = os.path.join(managed_folder, 'Metadata', 'Movies', safe_title)
        filepath = os.path.join(movie_dir, safe_title+'.strm')
        os.system('mkdir "%s"' % movie_dir)
        os.system('echo "" > "%s"' % filepath) # needs video file to be recognized by MediaElch.  Not using real path since it will likely become outdated

class EpisodeItem(ContentItem):

    def __init__(self, path, title, mediatype, show_title):
        self.show_title = show_title.encode('utf-8')
        super(EpisodeItem, self).__init__(path, title, mediatype)

    def __str__(self):
        return '[B]%s[/B] - [I]%s[/I]' % (self.title, self.path)

    def add_to_library(self):
        #TODO: handle exception when no folder in metadata
        # check if tvshow folder already exists
        self.rename_using_metadata()
        safe_showtitle = clean(self.show_title)
        metadata_dir = os.path.join(managed_folder, 'Metadata', 'TV', safe_showtitle)
        show_dir = os.path.join(managed_folder, 'ManagedTV', safe_showtitle)
        # if not, create folder, and copy tvshow.nfo and artwork
        if not os.path.exists(show_dir):
            os.system('mkdir "%s"' % show_dir)
            files = os.listdir(metadata_dir)
            for fname in files:
                if not (fnmatch(fname, '*[0-9]x[0-9]*') or fnmatch(fname, '*[Ss][0-9]*[Ee][0-9]*')):
                    os.system( 'ln -s "{0}" "{1}"'.format(os.path.join(metadata_dir, fname), os.path.join(show_dir, fname)))
        # link stream file and related thumb/nfo
        safe_title = clean(self.title)
        filepath = os.path.join(show_dir, safe_title+'.strm')
        os.system('echo "{0}" > "{1}"'.format(self.path, filepath) )
        os.system('ln -s "{0}.nfo" "{1}"'.format(os.path.join(metadata_dir, safe_title), show_dir) )
        os.system('ln -s "{0}-thumb.jpg" "{1}"'.format(os.path.join(metadata_dir, safe_title), show_dir) )
        # remove from staged, add to managed
        self.add_to_managed_file()
        self.remove_from_staged()

    def remove_from_library(self):
        # delete stream, nfo & thumb
        safe_showtitle = clean(self.show_title)
        safe_title = clean(self.title)
        show_dir = os.path.join(managed_folder, 'ManagedTV', safe_showtitle)
        #os.remove(os.path.join(show_dir, safe_title))
        os.system('rm "%s"*' % os.path.join(show_dir, safe_title))
        # check if last stream file, and remove entire dir if so
        files = os.listdir(show_dir)
        remove_dir = True
        for fname in files:
            if '.strm' in fname:
                remove_dir = False
                break
        if remove_dir:
            os.system('rm -r "%s"' % show_dir)
        # remove from managed list
        self.remove_from_managed()

    def create_metadata_item(self):
        #!TODO: shouldn't rename if it's not staged yet...
        #TODO: automatically call this when staging
        #TODO: actually create basic nfo file with name and (incorrect) episode number, and thumb if possible
        #?TODO: could probably just rename based on existing strm file instead of nfo file (should make a difference though)
        # create show_dir in Metadata/TV if it doesn't already exist
        safe_showtitle = clean(self.show_title)
        show_dir = os.path.join(managed_folder, 'Metadata', 'TV', safe_showtitle)
        if not os.path.exists(show_dir):
            os.system('mkdir "%s"' % show_dir)
        # check for existing stream file
        safe_title = clean(self.title)
        strm_path = os.path.join(show_dir, safe_title+'.strm')
        # only create metadata item if it doesn't already exist (by checking for stream title)
        if not os.path.exists(strm_path):
            # rename file if old nfo file has episode id
            old_renamed = glob(os.path.join(show_dir, '*[0-9]x[0-9]* - {0}.nfo'.format(safe_title)))
            if old_renamed:
                # prepend title with epid if so
                epid = old_renamed[0].split('/')[-1].replace(safe_title+'.nfo','')
                new_title = epid + self.title
            elif not (fnmatch(safe_title, '*[0-9]x[0-9]*') or fnmatch(safe_title, '*[Ss][0-9]*[Ee][0-9]*')):
                # otherwise, append -0x0 if title doesn't already have episode id (so media managers recognize it)
                new_title = self.title + '-0x0'
            else:
                new_title = self.title
            # create a blank file so media managers can recognize it and create nfo file
            filepath = os.path.join(show_dir, clean(new_title)+'.strm')
            os.system('echo "" > "%s"' % filepath)
            # refresh item in staged file if name changed
            if new_title != self.title:
                self.title = new_title
                self.remove_from_staged()
                self.add_to_staged_file()

    def rename(self, name):
        #TODO: CHANGE "%s"*.ext to "%s.ext" once library is rebuilt
        safe_showtitle = clean(self.show_title)
        safe_title = clean(self.title)
        metadata_dir = os.path.join(managed_folder, 'Metadata', 'TV', safe_showtitle)
        # define "title paths" (paths without extensions)
        title_path = os.path.join(metadata_dir, safe_title)
        new_title_path = os.path.join(metadata_dir, clean(name))
        # rename stream placeholder, nfo file, and thumb
        os.system('mv "%s"*.strm "%s.strm"' % (title_path, new_title_path))
        os.system('mv "%s"*.nfo "%s.nfo"' % (title_path, new_title_path))
        os.system('mv "%s"*-thumb.jpg "%s-thumb.jpg"' % (title_path, new_title_path))
        # rename property and refresh in staged file
        self.title = name
        self.remove_from_staged()
        self.add_to_staged_file()

    def rename_using_metadata(self):
        #?TODO: rename show_title too
        safe_showtitle = clean(self.show_title)
        safe_title = clean(self.title)
        metadata_dir = os.path.join(managed_folder, 'Metadata', 'TV', safe_showtitle)
        nfo_path = os.path.join(metadata_dir,  safe_title+'.nfo')
        log_msg('nfo_path: %s' % nfo_path, xbmc.LOGNOTICE)
        # only rename if nfo file exists
        if os.path.exists(nfo_path):
            # open nfo file and get xml soup
            with open(nfo_path) as fp:
                soup = BeautifulSoup(fp)
            # check for season & episode tags
            season = int(soup.find('season').get_text())
            episode = int(soup.find('episode').get_text())
            #ep_title = str(soup.find('title').get_text())  # can't use nfo episode title because "create_metadata_item" wouldn't recognize it
            # format into episode id
            epid = '{0:02}x{1:02} - '.format(season, episode)
            log_msg('epid: %s' % epid, xbmc.LOGNOTICE)
            # only rename if epid not already in name (otherwise it would get duplicated)
            if epid not in safe_title:
                new_title = epid + safe_title.replace('-0x0','')
                self.rename(new_title)
            elif '-0x0' in safe_title:
                new_title = safe_title.replace('-0x0','')
                self.rename(new_title)

    def get_show_title(self):
        return self.show_title
