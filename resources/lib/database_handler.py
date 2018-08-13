#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Defines the DatabaseHandler class
'''

import sqlite3

import resources.lib.utils as utils
from resources.lib.items.blocked import BlockedItem
from resources.lib.items.episode import EpisodeItem
from resources.lib.items.movie import MovieItem
from resources.lib.items.synced import SyncedItem


class DatabaseHandler(object):
    ''' Opens a connection with the SQLite file
    and provides methods for interfacing with database.
    SQLite connection is closed when object is deleted '''

    #TODO: Reimplement blocked keywords
    #TODO: Combine remove_content_item functions using **kwargs

    def __init__(self):
        # Connect to database
        self.conn = sqlite3.connect(utils.DATABASE_FILE)
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
        # Create tables if they doesn't exist
        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS Content
            (Directory TEXT PRIMARY KEY, Title TEXT,
            Mediatype TEXT, Status TEXT, Show_Title TEXT)'''
        )
        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS Synced
            (Directory TEXT PRIMARY KEY, Label TEXT, Type TEXT)'''
        )
        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS Blocked
            (Value TEXT NOT NULL, Type TEXT NOT NULL)'''
        )
        self.conn.commit()

    def __del__(self):
        # Close connection when deleted
        self.conn.close()

    @staticmethod
    def content_item_from_db(item):
        ''' Static method that converts Content query output to ContentItem subclass '''
        if item[2] == 'movie':
            return MovieItem(item[0], item[1], 'movie')
        elif item[2] == 'tvshow':
            return EpisodeItem(item[0], item[1], 'tvshow', item[4])
        raise ValueError('Unrecognized Mediatype in Content query')

    @utils.utf8_args
    @utils.logged_function
    def add_blocked_item(self, value, mediatype):
        ''' Add an item to Blocked with the specified values '''
        # Ignore if already in table
        if not self.check_blocked(value, mediatype):
            # Insert into table
            self.cur.execute("INSERT INTO Blocked (Value, Type) VALUES (?, ?)", (value, mediatype))
            self.conn.commit()

    @utils.utf8_args
    @utils.logged_function
    def add_content_item(self, path, title, mediatype, show_title=None):
        ''' Add item to Content with given parameters '''
        # Define sql command string
        sql_comm = '''INSERT OR IGNORE INTO Content
            (Directory, Title, Mediatype, Status, Show_Title)
            VALUES (?, ?, ?, 'staged', {0})'''
        params = (path, title, mediatype)
        # Format comamnd & params depending on movie or tvshow
        if mediatype == 'tvshow':
            sql_comm = sql_comm.format('?')
            params += (show_title, )
        else:
            sql_comm = sql_comm.format('NULL')
        # Execute and commit sql command
        self.cur.execute(sql_comm, params)
        self.conn.commit()
        # Optionally add item to directory, depending on settings and metadata items
        if mediatype == 'movie' and utils.AUTO_ADD_MOVIES != utils.NEVER:
            if utils.AUTO_ADD_MOVIES == utils.ALWAYS:
                MovieItem(path, title, 'movie').add_to_library()
            elif utils.AUTO_ADD_MOVIES == utils.WITH_METADATA:
                MovieItem(path, title, 'movie').add_to_library_if_metadata()
        elif mediatype == 'tvshow' and utils.AUTO_ADD_TVSHOWS != utils.NEVER:
            if utils.AUTO_ADD_TVSHOWS == utils.WITH_EPID:
                EpisodeItem(path, title, 'tvshow', show_title).add_to_library()
            elif utils.AUTO_ADD_TVSHOWS == utils.WITH_METADATA:
                EpisodeItem(path, title, 'tvshow', show_title).add_to_library_if_metadata()

    @utils.utf8_args
    @utils.logged_function
    def add_synced_dir(self, label, path, mediatype):
        ''' Create an entry in Synced with specified values '''
        self.cur.execute(
            "INSERT OR REPLACE INTO Synced (Directory, Label, Type) VALUES (?, ?, ?)",
            (path, label, mediatype)
        )
        self.conn.commit()

    @utils.utf8_args
    @utils.logged_function
    def check_blocked(self, value, mediatype):
        ''' Return True if the given entry is in Blocked '''
        self.cur.execute('SELECT (Value) FROM Blocked WHERE Value=? AND Type=?', (value, mediatype))
        res = self.cur.fetchone()
        return bool(res)

    @utils.logged_function
    def get_all_shows(self, status):
        ''' Query Content table for all (not null) distinct show_titles
        and cast results as list of strings '''
        # Query database
        self.cur.execute(
            '''SELECT DISTINCT Show_Title FROM Content WHERE Status=?
            ORDER BY (CASE WHEN Show_Title LIKE 'the %' THEN substr(Show_Title,5)
            ELSE Show_Title END) COLLATE NOCASE''', (status, )
        )
        # Get results and return items as list
        rows = self.cur.fetchall()
        return [x[0] for x in rows if x[0] is not None]

    @utils.logged_function
    def get_blocked_items(self):
        ''' Return all items in Blocked as a list of BlockedItem objects '''
        self.cur.execute("SELECT * FROM Blocked ORDER BY Type, Value")
        rows = self.cur.fetchall()
        return [BlockedItem(*x) for x in rows]

    @utils.logged_function
    def get_content_items(self, **kwargs):
        ''' Query Content table for sorted items with given constaints
        and casts results as ContentItem subclass

        keyword arguments:
            mediatype: string, 'movie' or 'tvshow'
            status: string, 'managed' or 'staged'
            show_title: string, any show title
            order: string, any single column '''
        # Define template for this sql command
        sql_templ = 'SELECT * FROM Content{c}{o}'
        # Define constraint and/or order string usings kwargs
        c_list = []
        params = ()
        order = ''
        for key, val in kwargs.iteritems():
            if key == 'status':
                c_list.append('Status=?')
                params += (val, )
            elif key == 'mediatype':
                c_list.append('Mediatype=?')
                params += (val, )
            elif key == 'show_title':
                c_list.append('Show_Title=?')
                params += (val, )
            elif key == 'order':
                order = ''' ORDER BY (CASE WHEN {0} LIKE 'the %' THEN substr({0},5)
                    ELSE {0} END) COLLATE NOCASE'''.format(val)
        command = ' WHERE ' + ' AND '.join(c_list) if c_list else ''
        # Format and execute sql command
        sql_comm = sql_templ.format(c=command, o=order)
        self.cur.execute(sql_comm, params)
        # Get results and return items as content items
        rows = self.cur.fetchall()
        return [self.content_item_from_db(x) for x in rows]

    @utils.utf8_args
    @utils.logged_function
    def get_synced_dirs(self, synced_type=None):
        ''' Get all items in Synced cast as a list of dicts '''
        # Define template for this sql command
        sql_templ = 'SELECT * FROM Synced'
        params = ()
        if synced_type:
            sql_templ += ' WHERE Type=?'
            params = (synced_type, )
        sql_templ += ''' ORDER BY (CASE WHEN Label LIKE 'the %' THEN substr(Label,5)
            ELSE Label END) COLLATE NOCASE'''
        # query database
        self.cur.execute(sql_templ, params)
        # get results and return as list of dicts
        rows = self.cur.fetchall()
        return [SyncedItem(*x) for x in rows]

    @utils.utf8_args
    @utils.logged_function
    def load_item(self, path):
        ''' Query a single item with path and casts result as ContentItem subclass '''
        # query database
        self.cur.execute('SELECT * FROM Content WHERE Directory=?', (path, ))
        # get results and return items as object
        item = self.cur.fetchone()
        return self.content_item_from_db(item)

    @utils.utf8_args
    @utils.logged_function
    def path_exists(self, path, status=None, mediatype=None):
        ''' Return True if path is already in database (with given status) '''
        #TODO: consider adding mediatype as optional parameter
        #       might speed-up by adding additional constraint
        #TODO: test speed against a set from "get_content_paths"
        # Build sql command and parameters, adding status if provided
        sql_comm = 'SELECT (Directory) FROM Content WHERE Directory=?'
        params = (path, )
        if status:
            sql_comm += ' AND Status=?'
            params += (status, )
        if mediatype:
            sql_comm += ' AND Mediatype=?'
            params += (mediatype, )
        self.cur.execute(sql_comm, params)
        # Get result and return True if result is found
        res = self.cur.fetchone()
        return bool(res)

    @utils.logged_function
    def remove_all_content_items(self, status, mediatype):
        ''' Remove all items from Content with status and mediatype '''
        # delete from table
        self.cur.execute("DELETE FROM Content WHERE Status=? AND Mediatype=?", (status, mediatype))
        self.conn.commit()

    @utils.utf8_args
    @utils.logged_function
    def remove_all_show_episodes(self, status, show_title):
        ''' Remove all tvshow items from Content with status and show_title '''
        # delete from table
        self.cur.execute(
            "DELETE FROM Content WHERE Status=? AND Show_Title=?",
            (status, show_title)
        )
        self.conn.commit()

    @utils.logged_function
    def remove_all_synced_dirs(self):
        ''' Delete all entries in Synced '''
        # remove all rows
        self.cur.execute('DELETE FROM Synced')
        self.conn.commit()

    @utils.utf8_args
    @utils.logged_function
    def remove_blocked(self, value, mediatype):
        ''' Remove the item in Blocked with the specified parameters '''
        self.cur.execute('DELETE FROM Blocked WHERE Value=? AND Type=?', (value, mediatype))
        self.conn.commit()

    @utils.utf8_args
    @utils.logged_function
    def remove_content_item(self, path):
        ''' Remove the item in Content with specified path '''
        # delete from table
        self.cur.execute("DELETE FROM Content WHERE Directory=?", (path, ))
        self.conn.commit()

    @utils.utf8_args
    @utils.logged_function
    def remove_synced_dir(self, path):
        ''' Remove the entry in Synced with the specified Directory '''
        # remove entry
        self.cur.execute("DELETE FROM Synced WHERE Directory=?", (path, ))
        self.conn.commit()

    @utils.utf8_args
    @utils.logged_function
    def update_content(self, path, **kwargs):
        ''' Update a single field for item in Content with specified path '''
        #TODO: Verify there's only one entry in kwargs
        sql_comm = "UPDATE Content SET {0}=(?) WHERE Directory=?"
        params = (path, )
        for key, val in kwargs.iteritems():
            if key == 'status':
                sql_comm = sql_comm.format('Status')
            elif key == 'title':
                sql_comm = sql_comm.format('Title')
            params = (val, ) + params
        # update item
        self.cur.execute(sql_comm, params)
        self.conn.commit()
