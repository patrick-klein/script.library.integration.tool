#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Filesystem utils for Windows/Linux'''

import os
from os import remove
from os import listdir
from os import symlink

from pathlib import Path
from shutil import rmtree
from shutil import copyfile

from os.path import dirname
from os.path import basename
from os import name as osname

from os.path import join
from os.path import isdir
from os.path import isfile


class CreateNfo(object):
    '''Module to create a .nfo file'''
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
                            '\t<season>{0}</season>\n'.format(self.jsondata['season_number']),
                            '\t<episode>{0}</episode_number>\n'.format(self.jsondata['season_number']),
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
    '''Create stream file with plugin_path at filepath'''
    try:
        with open(filepath, "w+") as strm:
            strm.write(plugin_path)
            strm.close()
    except Exception as e:
        return False
    return True


if osname == 'posix':
    def softlink_file(src, dst):
        '''Symlink file at src to dst'''
        symlink(src, dst)


    def softlink_files_in_dir(src_dir, dst_dir):
        '''Symlink all files in src_dir using wildcard to dst_dir'''
        for file in listdir(src_dir):
            try:
                symlink(join(src_dir, file), join(dst_dir, file))
            except OSError:
                pass
else:
    def softlink_file(src, dst):
        '''Copy file at src to dst'''
        # Can only symlink on unix, just copy file
        copyfile(src, dst)


    def softlink_files_in_dir(src_dir, dst_dir):
        '''Symlink all files in src_dir using wildcard to dst_dir'''
        # Can only symlink on unix, just copy files
        for file in listdir(src_dir):
            copyfile(join(src_dir, file), join(dst_dir, file))


def mkdir(dir_path):
    '''Create a directory'''
    Path(dir_path).mkdir(
        mode=0o755,
        parents=True,
        exist_ok=True
    )


# def mv_with_type(title_path, filetype, title_dst):
#     '''Move files with wildcard between title_path & filetype to title_dst'''
#     os.system('mv "{0}"*{1} "{2}{1}"'.format(title_path, filetype, title_dst))


def delete_strm(path_to_remove):
    '''Remove one or more strm files'''
    if isdir(path_to_remove):
        rm_files = [strm_file for strm_file in os.listdir(
            path_to_remove) if ".strm" in strm_file]
        for file in rm_files:
            remove(file)
    elif isfile(path_to_remove):
        remove(path_to_remove)


def delete_with_wildcard(title_path):
    '''Remove all files starting with title_path using wildcard'''
    wildcard = basename(title_path)

    for file in os.listdir(dirname(title_path)):
        if wildcard in file:
            os.remove(file, dir_fd=None)


def remove_dir(dir_path):
    '''Remove directory at dir_path'''
    rmtree(dir_path, ignore_errors=False, onerror=None)
