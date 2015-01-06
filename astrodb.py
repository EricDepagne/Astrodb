#!/usr/bin/python
# -*- coding: utf-8 -*-

# python imports
import sys

# sql import
import psycopg2

user = 'postgres'
passwd = 'postgres'
host = 'localhost'
port = 5432

# Connection to the local database.
conn = psycopg2.connect(database="Astronomy",
                        user=user,
                        password=passwd,
                        host=host,
                        port=port)
cursor = conn.cursor()

# First, we list all tables available in the database.
cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
listoftables = cursor.fetchall()
