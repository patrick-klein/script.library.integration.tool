#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Filesystem utils for Windows/Linux."""

import os
from os import remove

from pathlib import Path
from shutil import rmtree

from os.path import dirname
from os.path import basename

from os.path import isdir
from os.path import isfile
from os.path import exists

from resources.lib.log import log_msg


class CreateNfo(object):
    """
    Module to create a .nfo file.

    Future possible new keys:
        title, showtitle, year, runtime, thumb aspect="poster"
        thumb aspect="poster" season="1" type="season", id, imdbid.
    """

    def __init__(self, _type, filepath, jsondata):
        """__init__ CreateNfo."""
        self.type = _type
        self.filepath = filepath
        self.jsondata = jsondata
        self.root = ''.join(
            [
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n',
                '<{0}>\n%s</{1}>'.format(self.type, self.type)
            ]
        )

        self.create()

    def tvshow(self):
        """Create tvshow nfo file."""
        try:
            return ''.join(
                [
                    '\t<title>{0}</title>\n'.format(
                        self.jsondata['showtitle']),
                    '\t<showtitle>{0}</showtitle>\n'.format(
                        self.jsondata['showtitle']),
                    '\t<year>{0}</year>\n'.format(self.jsondata['year'])
                ]
            )
        except KeyError:
            pass

    def episodedetails(self):
        """
        Create episodedetails nfo for tvshow.

        Future possible new keys:
            id, uniqueid default="true" type="tvdb", runtime, thumb.
        """
        try:
            return ''.join(
                [
                    '\t<title>{0}</title>\n'.format(self.jsondata['title']),
                    '\t<showtitle>{0}</showtitle>\n'.format(
                        self.jsondata['showtitle']),
                    '\t<season>{0}</season>\n'.format(self.jsondata['season']),
                    '\t<episode>{0}</episode_number>\n'.format(
                        self.jsondata['season']),
                    '\t<year>{0}</year>\n'.format(self.jsondata['year']),
                    '\t<original_filename>{0}</original_filename>\n'.format(
                        self.jsondata['file'])
                ]
            )
        except KeyError:
            pass

    def movie(self):
        """
        Create movie nfo.

        future possible new keys:
            runtime, thumb aspect="poster", fanart, thumb, id, tmdbid.
        """
        try:
            return ''.join(
                [
                    '\t<title>{0}</title>\n'.format(
                        self.jsondata['title']),
                    '\t<year>{0}</year>\n'.format(self.jsondata['year']),
                    '\t<original_filename>{0}</original_filename>\n'.format(
                        self.jsondata['file'])
                ]
            )
        except KeyError:
            pass

    def create(self):
        """
        Create the nfo file.

        element root: movie, tvshow or episodedetails
        tvshow            title, showtitle
        movie             title
        episodedetails    title, showtitle.
        """
        body = self.tvshow() or self.episodedetails() or self.movie()
        self.root = self.root % body
        with open(self.filepath, "w+") as nfofile:
            try:
                nfofile.write(self.root)
            except Exception as e:
                log_msg(e)
                raise e
            finally:
                nfofile.close()


def create_stream_file(plugin_path, filepath):
    """Create stream file with plugin_path at filepath."""
    with open(filepath, "w+") as strm:
        try:
            strm.write(plugin_path)
        except Exception as e:
            log_msg(e)
            return False
        finally:
            strm.close()
    return True


def mkdir(dir_path):
    """Create a directory."""
    try:
        Path(dir_path).mkdir(
            mode=0o755,
            parents=True,
            exist_ok=True
        )
    except Exception as e:
        raise e

# def mv_with_type(title_path, filetype, title_dst):
#     """Move files with wildcard between title_path & filetype to title_dst."""
#     os.system('mv "{0}"*{1} "{2}{1}"'.format(title_path, filetype, title_dst))


def delete_strm(path_to_remove):
    """Remove one or more strm files."""
    if isdir(path_to_remove):
        rm_files = [
            strm_file for strm_file in os.listdir(
                path_to_remove
            ) if ".strm" in strm_file
        ]
        for file in rm_files:
            remove(file)
    elif isfile(path_to_remove):
        remove(path_to_remove)


def delete_with_wildcard(title_path):
    """Remove all files starting with title_path using wildcard."""
    wildcard = basename(title_path)
    directory = dirname(title_path)
    if exists(directory):
        for file in os.listdir(dirname(directory)):
            if wildcard in file:
                try:
                    os.remove(file, dir_fd=None)
                except FileNotFoundError:
                    pass


def remove_dir(dir_path):
    """Remove directory at dir_path."""
    try:
        rmtree(dir_path, ignore_errors=False, onerror=None)
    except FileNotFoundError:
        pass
