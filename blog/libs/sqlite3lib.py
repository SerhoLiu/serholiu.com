#!/usr/bin/env python

import sqlite3
import itertools


class Connection(object):
    """
    A lightweight wrapper around sqlite3; based on tornado.database
    
    db = sqlite.Connection("filename")
    for article in db.query("SELECT * FROM articles")
        print article.title
      
    Cursors are hidden by the implementation.
    """
  
    def __init__(self, filename, isolation_level=None):
        self.filename = filename
        self.isolation_level = isolation_level  # None = autocommit
        self._db = None
        try:
            self.reconnect()
        except:
            # log error @@@
            raise
      
    def close(self):
        """Close database connection"""
        if getattr(self, "_db", None) is not None:
            self._db.close()
        self._db = None
      
    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._db = sqlite3.connect(self.filename)
        self._db.isolation_level = self.isolation_level
    
    def _cursor(self):
        """Returns the cursor; reconnects if disconnected."""
        if self._db is None:
            self.reconnect()
        return self._db.cursor()
    
    def __del__(self):
        self.close()
    
    def execute(self, query, *parameters):
        """Executes the given query, returning the lastrowid from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()
      
    def executemany(self, query, parameters):
        """Executes the given query against all the given param sequences"""
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()
      
    def _execute(self, cursor, query, parameters):
        try:
            return cursor.execute(query, parameters)
        except OperationalError:
            # log error @@@
            self.close()
            raise
      
    def query(self, query, *parameters):
        """Returns a row list for the given query and parameters."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            column_names = [d[0] for d in cursor.description]
            return [Row(itertools.izip(column_names, row)) for row in cursor]
        finally:
            # cursor.close()
            pass
      
    def get(self, query, *parameters):
        """Returns the first row returned for the given query."""
        rows = self.query(query, *parameters)
        if not rows:
            return None
        elif len(rows) > 1:
            raise Exception("Multiple rows returned from sqlite.get() query")
        else:
            return rows[0]
      

class Row(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
      
OperationalError = sqlite3.OperationalError
