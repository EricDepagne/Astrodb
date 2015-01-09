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
# We list all the columns in each table.
DBScheme = {}
for i in listoftables:
    cursor.execute("select * from %s limit 0", (AsIs(i[0]),))
    colnames = [desc[0] for desc in cursor.description if desc[0] != 'id']
    d = {i[0]: colnames}
    DBScheme.update(d)


def info(star):
    id = getid('stars', star)
    tables = []
    for key in DBScheme.keys():
        if key != 'stars':
            tables.append(key)
    # print tables
    for table in tables:
        #print DBScheme[table]
        #print cursor.mogrify("select %s from %s where id=%s", (AsIs(DBScheme[table][0]), AsIs(table), id))
        cursor.execute("select %s from %s where id=%s", (AsIs(DBScheme[table][0]), AsIs(table), id))
        res = cursor.fetchall()
        print table, res


def database(action, tableout, star, field, value, tablein='stars'):

    # Verifying the validity of the input.
    validity = 0
    if tableout not in DBScheme.keys():
        validity = 1
    if tableout in DBScheme.keys() and field not in DBScheme[tableout]:
        validity = 2
    if validity:
        if validity == 1:
            print("Table {0} does not exist. Try one of {1}".format(tableout, DBScheme.keys()))
        if validity == 2:
            print ("Field {0} in table {1} does not exist. Try one of {2}".format(field, tableout, DBScheme[tableout]))
        #sys.exit("Input not matching the database, exiting")
    # Input is valid, let´ s proceed.

    if action == 'delete' or action == 'del':
        removeparameter(tablein, tableout, star, field, value)
    elif action == 'insert':
        addparameter(tablein, tableout, star, field, value)
    else:
        print("Action should be : delete or insert. Or use the function list() to get all infos concerning one object.")


def removeparameter(tablein, tableout, star, field, value):
    id = getid(tablein, star)
    present = checkentry(tableout, field, id, value)

    if present:
        print("Deleting {0} in table {1} for star {2}".format(value, tableout, star))
        cursor.execute(" delete from %s where id=(%s) and %s = (%s)", (AsIs(tableout), id, AsIs(field), value))
    else:
        print("Value {0} not in table {1} for star {2}".format(value, tableout, star))
    connection.commit()


def addparameter(tablein, tableout, star, field, value):
    """ Add a parameter for a given star into the proper table

    """
# Get the ID of the star
    id = getid(tablein, star)
    present = checkentry(tableout, field, id, value)
    print present
    if type(field) is not tuple or type(value) is not tuple:
        field = tuple(field)
        value = (value,)
# Preparing the SQL query.
# query template
    SQL = "insert into %s %s values %s"
# Preparing the data
    t1 = AsIs(tableout)
    v1 = tuple([AsIs(i) for i in value + (id,)])
    f1 = tuple([AsIs(i) for i in field + ('id',)])
    data = (t1, f1, v1)
    present = False

    if not present:
        print(cursor.mogrify(SQL, data))
        cursor.execute(SQL, data)
        #cursor.execute("insert into %s %s values (%s)", (AsIs(tableout), AsIs(f), v))

        #cursor.execute("insert into %s (id, %s) values ((%s), (%s) )", (AsIs(tableout), AsIs(field), id, value))
    else:
        print("Value {0} already in table {1} for star {2}".format(value, tableout, star))
    connection.commit()


def checkentry(table, field, id, value):
    present = False
    print ("Checking input data: {0}, {1}, {2}".format(table, field, value))
    if len(field) != len(value):
        sys.exit()
    SQL = "select %s from %s where id = %s"
    t1 = AsIs(table)
    f1 = tuple([AsIs(i) for i in field])
    data = (f1, t1, id)
    print data
    cursor.execute(SQL, data)
    result = cursor.fetchall()
#    for i in range(len(field)):
#        print field[i]
#        print value[i]
#    # We extract all the values for a given star from the correct table
#    #print cursor.mogrify("select %s from %s where id=%s", (AsIs(field), AsIs(table), id))
#        cursor.execute("select %s from %s where id=%s", (AsIs(field[i]), AsIs(table[i]), id))
#        result = cursor.fetchall()
#        print result

# We check that the value to be insered is not here already.
    present = False
    for i, v in enumerate(result):
        print i,v, value
        if value in v:
            present = True
    return present


def getid(tablein, star):
    # Penser `a verifier que l'étoile existe.
    cursor.execute("select id from %s where name = (%s)", (AsIs(tablein), star))
    return cursor.fetchall()[0][0]
