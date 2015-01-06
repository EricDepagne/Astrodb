#!/usr/bin/python
# -*- coding: utf-8 -*-

# python imports
import sys

# sql import
import psycopg2
from psycopg2.extensions import AsIs

user = 'postgres'
passwd = 'postgres'
host = 'localhost'
port = 5432

# Connection to the local database.
connection = psycopg2.connect(database="Astronomy",
                              user=user,
                              password=passwd,
                              host=host,
                              port=port)
cursor = connection.cursor()

# First, we list all tables available in the database.
cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
listoftables = cursor.fetchall()


def addparameter(tablein, tableout, star, type, value):
    """ Add a parameter for a given star
    into the proper table
    """
# Get the ID of the star first
    id = getid(tablein, star)
    print id
    cursor.execute("insert into temperatures (id, temperature) values ((%s), (%s) )", (id, value))

    print"{0} {1} {2} {3} {4}".format(tablein, tableout, star, type, value)
    connection.commit()


def getid(tablein, star):
    # Penser `a verifier que l'étoile existe.
    cursor.execute("select id from %s where name = (%s)", (AsIs(tablein), star))
    return cursor.fetchall()[0][0]
