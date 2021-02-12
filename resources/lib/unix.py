#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
System commands for posix/unix systems
'''

# TODO: Get rid of this module

import os
from os import listdir, symlink
from os.path import join


class CreateNfo(object):
    ''' Module to create a .nfo file '''
    # this module is necessary becouse xml.etree.ElementTree 
    # return error with unicode charters
    def __init__(self, nfotype, filepath, jsondata):
        self.nfotype = nfotype
        self.filepath = filepath
        self.jsondata = jsondata

        try:
            self.create()
        except Exception as e:
            raise e

    def create(self):
        file = open(self.filepath, "w+")
        root = ''.join(['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n',
                        '<{0}>\n%s</{1}>'.format(self.nfotype, self.nfotype)])
        # element root: movie, tvshow or episodedetails
        # tvshow            title, showtitle
        # movie             title
        # episodedetails    title, showtitle
        if self.nfotype == 'tvshow':
            # future possible new keys:
            # title, showtitle, year, runtime, thumb aspect="poster"
            # thumb aspect="poster" season="1" type="season", id, imdbid
            body = ''.join(['\t<title>{0}</title>\n'.format(self.jsondata['show_title']),
                            '\t<showtitle>{0}</showtitle>\n'.format(self.jsondata['show_title']),
                            '\t<year>{0}</year>\n'.format(self.jsondata['year']),])
        elif self.nfotype == 'episodedetails':
            # future possible new keys:
            # id, uniqueid default="true" type="tvdb", runtime, thumb
            body = ''.join(['\t<title>{0}</title>\n'.format(self.jsondata['episode_title']),
                            '\t<showtitle>{0}</showtitle>\n'.format(self.jsondata['show_title']),
                            '\t<season>{0}</season>\n'.format(self.jsondata['seasonnum']),
                            '\t<episode>{0}</episodenum>\n'.format(self.jsondata['seasonnum']),
                            '\t<year>{0}</year>\n'.format(self.jsondata['year']),
                            '\t<original_filename>{0}</original_filename>\n'.format(self.jsondata['link_stream_path'])])
        elif self.nfotype == 'movie':
            # future possible new keys:
            # runtime, thumb aspect="poster", fanart, thumb, id, tmdbid
            body = ''.join(['\t<title>{0}</title>\n'.format(self.jsondata['movie_title']),
                        '\t<year>{0}</year>\n'.format(self.jsondata['year']),
                        '\t<original_filename>{0}</original_filename>\n'.format(self.jsondata['link_stream_path'])])
        root = root % body
        file.write(root)
        file.close()

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
