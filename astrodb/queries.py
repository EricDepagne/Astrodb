# -*- coding: utf-8 -*-
"""
Some stuff to query the database
"""

# sql import
import psycopg2
from psycopg2.extensions import AsIs

# Astro imports
from astropy.coordinates import SkyCoord
from astropy import units as u


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


def listofstars():
    """
    Gives a list of all stars in the database
    """
    cursor.execute("select name from stars")
    res = cursor.fetchall()
    return [i[0] for i in res]


def update(star, ra, dec):
    """
    Update the ra and dec for a star, if need be
    """
    c = SkyCoord(ra=ra*u.degree, dec=dec*u.degree)
    cursor.execute("update stars set right_ascension = %s, declination = %s where name = %s", (AsIs(c.ra.degree), AsIs(c.dec.degree), star))
    connection.commit()
    return


def newstar(star):
    """
    Add a new star in the data base
    """
    print (star)
    cursor.execute("insert into stars (name) values (%s)", (star,))
    connection.commit()


def info(star):
    """
    lists all attributes of the star
    """
    id = getid('stars', star)
    tables = []
    data = {}
    for key in DBScheme.keys():
        # `print len(DBScheme[key]), DBScheme[key][0]
        for i in range(len(DBScheme[key])):
            data.update({DBScheme[key][i]: ''})
    for key in DBScheme.keys():
        tables.append(key)
    for table in tables:
        # print table, DBScheme[table]
# preparing the query
        d = {key: AsIs(key) for key in DBScheme[table]}
        l = ['%('+key+')s' for key in DBScheme[table]]
        p = ', '.join(x for x in l)
        #p = "("+p+")"

        #print"d vaut : {0} et p vaut {1} et table {2}".format(d, p, table)
        query = "select " + p + " from " + table + " where id = " + str(id)
        print cursor.mogrify(query, d)
        cursor.execute(query, d)
        res = cursor.fetchall()
        if table == 'stars':
            c = SkyCoord(res[0][1], res[0][2], 'icrs', unit='deg')
            #print res[0][0], c.to_string('hmsdms')
        #else:
            #print res
        d = {table: res}
        data.update(d)

   # print test
    return data


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
# Preparing the delete SQL query.

#    query = '%(row0)s = %(value0)s'
    query = ""
    prefix = ""
    test = {'table': AsIs(tableout)}
    if isinstance(field, str):
        parameternumber = 1
    if isinstance(field, tuple):
        parameternumber = len(field)
    for i in range(parameternumber):
        row = 'row'+str(i)
        val = 'value'+str(i)
        if i > 0:
            prefix = " and "
        query = query + prefix + " %("+row+")s = %("+val+")s"
        try:
            test.update({row: AsIs(field[i])})
            test.update({val: AsIs(value[i])})
        except TypeError:
            test.update({row: AsIs(field)})
            test.update({val: AsIs(value)})

# query template
    SQL = "delete from %(table)s where " + query
    #print SQL, test
    # print (cursor.mogrify(SQL, test))
    # print present

    if present:
        print("Deleting {0} in table {1} for star {2}".format(value, tableout, star))
        # cursor.execute(" delete from %s where id=(%s) and %s = (%s)", (AsIs(tableout), id, AsIs(field), value))
        cursor.execute(SQL, test)
    else:
        print("Value {0} not in table {1} for star {2}".format(value, tableout, star))
    connection.commit()


def addparameter(tablein, tableout, star, field, value):
    """ Add a parameter for a given star into the proper table

    """
# Get the ID of the star
    id = getid(tablein, star)
    present = checkentry(tableout, field, id, value)
# Preparing the insert SQL query.
    query = ""
    rows = ""
    values = ""
    coma = ""
    test = {'table': AsIs(tableout)}
    if isinstance(field, str):
        parameternumber = 1
    if isinstance(field, tuple):
        parameternumber = len(field)
    for i in range(parameternumber):
        row = 'row'+str(i)
        val = 'value'+str(i)
        if i > 0:
            coma = ","
        rows = rows + coma + "%("+row+")s"
        values = values + coma + "%("+val+")s"
        try:
            test.update({row: AsIs(field[i])})
            test.update({val: AsIs(value[i])})
        except TypeError:
            test.update({row: AsIs(field)})
            test.update({val: AsIs(value)})
    rows = "(id, " + rows + ")"
    values = "(" + str(id) + ", " + values + ")"
    #print rows
    #print values
    #print test
    query = "%(table)s " + rows + " values " + values

# query template
    SQL = "insert into " + query
    #print SQL
    if not present:
        print(cursor.mogrify(SQL, test))
        cursor.execute(SQL, test)
        #cursor.execute("insert into %s %s values (%s)", (AsIs(tableout), AsIs(f), v))

        #cursor.execute("insert into %s (id, %s) values ((%s), (%s) )", (AsIs(tableout), AsIs(field), id, value))
    else:
        print("Value {0} already in table {1} for star {2}".format(value, tableout, star))
    connection.commit()


def checkentry(table, field, id, value):
    present = False
    print ("Checking input data: {0}, {1}, {2}".format(table, field, value))
    SQL = "select %s from %s where id = %s"
    t1 = AsIs(table)
    if isinstance(field, str):
        f1 = [AsIs(field)]
    if isinstance(field, tuple):
        f1 = [AsIs(i) for i in field]
    data = (f1, t1, id)
    cursor.execute(SQL, data)
    #print cursor.mogrify(SQL, data)
    result = cursor.fetchall()

# We check that the value to be insered is not here already.
    present = False
    # print value, result[0][0]
    for index, val in enumerate(result):
        try:
            if list(value) == result[index][0]:
                present = True
        except TypeError:
            if value == result[index][0][0]:
                present = True
    return present


def getid(tablein, star):
    # Penser `a verifier que l'étoile existe.
    cursor.execute("select id from %s where name = (%s)", (AsIs(tablein), star))
    return cursor.fetchall()[0][0]
