#!/usr/bin/python
# -*- coding: utf-8 -*-

# python imports
import sys

# sql import
import psycopg2
from psycopg2.extensions import AsIs

user = 'postgres'
host = 'localhost'
port = 5432

# Connection to the local database.
connection = psycopg2.connect(database="Astronomy",
                              user=user,
                              host=host,
                              port=port)
cursor = connection.cursor()

# First, we list all tables available in the database.
cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
listoftables = cursor.fetchall()


def addparameter(tablein, tableout, star, field, value):
    """ Add a parameter for a given star into the proper table

    Parameters :
    tablein : str

    tableout : str

    star : str

    field : str

    value :

    Output :
    None.
    """
# Get the ID of the star
    id = getid(tablein, star)
    present = checkentry(tableout, field, id, value)

    if not present:
        print("Inserting {0} in table {1} for star {2}".format(value, tableout, star))
        cursor.execute("insert into temperatures (id, temperature) values ((%s), (%s) )", (id, value))
    else :
        print("Value {0} already in table {1} for star {2}".format(value, tableout, star))
    connection.commit()


def checkentry(tablein, field, id, value):
    # First, we extract all the values for a given star from the correct table
    cursor.execute("select %s from %s where id=%s", (AsIs(field), AsIs(tablein), id))
    result = cursor.fetchall()

# Then, we´ re checking that the value to be insered is not here already.
    present = False
    for i, v in enumerate(result):
        if value in v:
            present = True

    return present


def getid(tablein, star):
    # Penser `a verifier que l'étoile existe.
    cursor.execute("select id from %s where name = (%s)", (AsIs(tablein), star))
    return cursor.fetchall()[0][0]
