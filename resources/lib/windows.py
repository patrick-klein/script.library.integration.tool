#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This module contains system commands for nt/windows systems
'''

import os

def create_empty_file(filepath):
    ''' creates empty file at filepath '''
    raise NotImplementedError('windows.create_empty_file() not implemented!')

def create_stream_file(plugin_path, filepath):
    ''' creates stream file with plugin_path at filepath '''
    raise NotImplementedError('windows.create_stream_file() not implemented!')

def softlink_file(src, dst):
    ''' symlink file at src to dst '''
    raise NotImplementedError('windows.softlink_file() not implemented!')

def softlink_files_in_dir(src_dir, dst_dir):
    ''' symlink all files in src_dir using wildcard to dst_dir '''
    raise NotImplementedError('windows.softlink_files_in_dir() not implemented!')

def mkdir(dir_path):
    ''' make directory at dir_path '''
    raise NotImplementedError('windows.mkdir() not implemented!')

def mv_with_type(title_path, filetype, title_dst):
    ''' moves files with wildcard between title_path & filetype to title_dst '''
    raise NotImplementedError('windows.mv_with_type() not implemented!')

def rm_strm_in_dir(dir_path):
    ''' removes all stream files in dir '''
    raise NotImplementedError('windows.rm_strm_in_dir() not implemented!')

def rm_with_wildcard(title_path):
    ''' removes all files starting with title_path using wildcard '''
    raise NotImplementedError('windows.rm_with_wildcard() not implemented!')

def remove_dir(dir_path):
    ''' removes directory at dir_path '''
    raise NotImplementedError('windows.remove_dir() not implemented!')
