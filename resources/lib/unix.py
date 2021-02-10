#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
System commands for posix/unix systems
'''

# TODO: Get rid of this module

import os
from os import listdir, symlink
from os.path import join, isfile

import xml.etree.ElementTree as et
from bs4 import BeautifulSoup

class CreateNfo(object):
    def __init__(self, nfotype, filepath, jsondata):
        self.nfo = et.Element(nfotype)
        self.nfotype = nfotype
        self.filepath = filepath
        self.jsondata = jsondata

        try:
            self.create()
            self.indent()
        except Exception as e:
            raise e

    def indent(self):
        with open(self.filepath, 'r') as nf:
            soup = BeautifulSoup(nf, 'html.parser')

            w_file = open(self.filepath, 'w')
            w_file.write(soup.prettify())
            w_file.close()
            print(soup.prettify(formatter="html"))
            nf.close()

    def create(self):
        if not isfile(self.filepath):
            file = open(self.filepath, "w+")
            file.close()

        # movie             title
        # tvshow            title, showtitle
        # episodedetails    title, showtitle
        # element root: movie, tvshow or episodedetails
        if self.nfotype == 'tvshow':
            title = et.Element('title')
            title.text = self.jsondata['show_title']

            show_title = et.Element('showtitle')
            show_title.text = self.jsondata['show_title']

            year = et.Element('year')
            year.text = self.jsondata['year']
            # future possible new keys:
            # title
            # showtitle
            # year
            # runtime
            # thumb aspect="poster"
            # thumb aspect="poster" season="1" type="season"
            # id
            # imdbid
            self.nfo.append(title)
            self.nfo.append(show_title)
            self.nfo.append(year)
        elif self.nfotype == 'episodedetails':
            title = et.Element('title')
            title.text = self.jsondata['episode_title'].decode('utf-8')
            
            show_title = et.Element('showtitle')
            show_title.text = self.jsondata['show_title'].decode('utf-8')

            season = et.Element('season')
            season.text = str(self.jsondata['seasonnum'])
            
            episode = et.Element('episode')
            episode.text = str(self.jsondata['episodenum'])

            year = et.Element('year')
            year.text = self.jsondata['year']

            original_filename = et.Element('original_filename')
            original_filename.text = self.jsondata['link_stream_path']            
            # future possible new keys:
            # id
            # uniqueid default="true" type="tvdb"
            # runtime
            # thumb
            self.nfo.append(title)
            self.nfo.append(show_title)
            self.nfo.append(season)
            self.nfo.append(episode)
            self.nfo.append(year)
            self.nfo.append(original_filename)
        elif self.nfotype == 'movie':
            title = et.Element('title')
            title.text = self.jsondata['movie_title']

            year = et.Element('year')
            year.text = self.jsondata['year']

            original_filename = et.Element('original_filename')
            original_filename.text = self.jsondata['link_stream_path']
            # future possible new keys:
            # runtime
            # thumb aspect="poster"
            # fanart
                # thumb
            # id
            # tmdbid
            self.nfo.append(title)
            self.nfo.append(year)
            self.nfo.append(original_filename)

        nfo_tree = et.ElementTree(self.nfo)
        nfo_tree.write(self.filepath, xml_declaration=True, encoding='utf-8', method='xml')


def create_stream_file(plugin_path, filepath):
    ''' Create stream file with plugin_path at filepath '''
    # os.system('echo "{0}" > "{1}"'.format(plugin_path, filepath))
    try:
        strm = open(filepath, "w+")
        strm.write(plugin_path)
        strm.close()
    except Exception as e:
        return False
    return True

def softlink_file(src, dst):
    ''' Symlink file at src to dst '''
    os.system('ln -s "{0}" "{1}"'.format(src, dst))


def softlink_files_in_dir(src_dir, dst_dir):
    ''' Symlink all files in src_dir using wildcard to dst_dir '''
    for file in listdir(src_dir):
        try:
            symlink(join(src_dir, file), join(dst_dir, file))
        except OSError:
            pass

def mkdir(dir_path):
    ''' Make directory at dir_path '''
    os.system('mkdir "{0}"'.format(dir_path))


def mv_with_type(title_path, filetype, title_dst):
    ''' Move files with wildcard between title_path & filetype to title_dst '''
    os.system('mv "{0}"*{1} "{2}{1}"'.format(title_path, filetype, title_dst))


def rm_strm_in_dir(dir_path):
    ''' Remove all stream files in dir '''
    os.system('rm "{0}/"*.strm'.format(dir_path))


def rm_with_wildcard(title_path):
    ''' Remove all files starting with title_path using wildcard '''
    os.system('rm "{0}"*'.format(title_path))


def remove_dir(dir_path):
    ''' Remove directory at dir_path '''
    os.system('rm -r "{0}"'.format(dir_path))
