#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This module contains system commands for posix/unix systems
'''

import os

def create_empty_file(filepath):
    ''' creates empty file at filepath '''
    os.system('echo "" > "{0}"'.format(filepath))

def create_stream_file(plugin_path, filepath):
    ''' creates stream file with plugin_path at filepath '''
    os.system('echo "{0}" > "{1}"'.format(plugin_path, filepath))

def softlink_file(src, dst):
    ''' symlink file at src to dst '''
    os.system('ln -s "{0}" "{1}"'.format(src, dst))

def softlink_files_in_dir(src_dir, dst_dir):
    ''' symlink all files in src_dir using wildcard to dst_dir '''
    os.system('ln -s "{0}/"* "{1}"'.format(src_dir, dst_dir))

def mkdir(dir_path):
    ''' make directory at dir_path '''
    os.system('mkdir "{0}"'.format(dir_path))

def mv_with_type(title_path, filetype, title_dst):
    ''' moves files with wildcard between title_path & filetype to title_dst '''
    os.system('mv "{0}"*{1} "{2}{1}"'.format(title_path, filetype, title_dst))

def rm_strm_in_dir(dir_path):
    ''' removes all stream files in dir '''
    os.system('rm "{0}/*.strm"'.format(dir_path))

def rm_with_wildcard(title_path):
    ''' removes all files starting with title_path using wildcard '''
    os.system('rm "{0}"*'.format(title_path))

def remove_dir(dir_path):
    ''' removes directory at dir_path '''
    os.system('rm -r "{0}"'.format(dir_path))
