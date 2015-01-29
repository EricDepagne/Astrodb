# -*- coding: utf-8 -*-
"""
Some stuff to query the database
"""
# Global imports
import sys

# Special imports
import collections

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
connection = psycopg2.connect(database="AstroTest",
                              user=user,
                              host=host,
                              port=port)
cursor = connection.cursor()

# First, we list all tables available in the database.
cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
# We list all the columns in each table.
DBScheme = {}
for i in cursor.fetchall():
    cursor.execute("select * from %s limit 0", (AsIs(i[0]),))
    colnames = [desc[0] for desc in cursor.description if desc[0] != 'id']
    d = {i[0]: colnames}
    DBScheme.update(d)


def usage():
    """
    Temporary help
    """
    print("""
    This module creates a series of functions to access and update a database of stars.
    The following functions are available:

    clean() : allows to put the database in a clean state, in case errors have occured.
    Parameters : None

    listofstars() : parses the stars table, and lists all entries there. It will give a complete list of stars that have been entered.
    Parameters : None
    Returns : list.

    newstar() : Creates a new entry in the stars table.

    newstar(star)
    Parameters
    star : string
    Example : newstar('Star1')

    update() : Used to enter the RA and DEC of a star.

    update(star, RA, DEC)
    Parameters :
    star : string
    RA : float
    DEC : float
    Example: update('Star1', 0.0, 0.0)

    database(): The main function of the module. Used to insert new data in the database but also to remove records from the database.

    database(action, table, star, field, value)

    Parameters:
    action : string. Either insert or delete.
    table :string. Where is the data to be inserted
    star : string. Name of the stars whose record is to be updated
    field : string. Property to be updated.
    value: string of float. The type depends on the property.

    Example :
    database('insert','temperatures', 'HE 1506-0113', 'temperature', 5016)
    database('insert', 'names', 'BS 16929-005', 'alternatenames', '2MASS J13032947+3351091' )


    """)


def clean():
    """
    Used to rollback the last query, in case it fails.
    """
    connection.rollback()


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
    RA and DEC should ne entered as floats.
    """
    print(ra, dec)
    try:
        SQL = 'update stars set right_ascension = (%s), declination = (%s) where name = (%s)'
        data = (ra, dec, star)
        cursor.execute(SQL, data)
        #cursor.execute("update stars set right_ascension = %s, declination = %s where name = %s", (AsIs(c.ra.degree), AsIs(c.dec.degree), star))
    except psycopg2.ProgrammingError:
        connection.rollback()
    connection.commit()
    return


def newstar(star):
    """
    Add a new star in the data base
    """
    star_id = getid(star)
# We are not interested in the real id of the star. If the return is not None, then the star exists already.
    if not star_id:
        cursor.execute("insert into stars (name) values (%s)", (star,))
    else:
        print("Star already exists")
    connection.commit()


def info(star):
    """
    lists all attributes of the star
    """
    id = getid(star)[0][0]
    tables = []
    data = {}

    for key in list(DBScheme.keys()):
        for i in range(len(DBScheme[key])):
            data.update({DBScheme[key][i]: ''})
    for key in list(DBScheme.keys()):
        tables.append(key)
    for table in tables:
# preparing the query
        d = {key: AsIs(key) for key in DBScheme[table]}
        l = ['%('+key+')s' for key in DBScheme[table]]
        p = ', '.join(x for x in l)

        star_id = 'star_id'
        if table == 'stars':
            star_id = 'id'
        query = "select " + p + " from " + table + " where " + star_id + " = " + str(id)
        #print cursor.mogrify(query, d)
        cursor.execute(query, d)
        res = cursor.fetchall()
        # print res
        if table == 'stars':
            # This is the only table with multiply unique columns.
            # print res[0][1], res[0][2]
            if not res[0][1]:
                continue
            c = SkyCoord(ra=res[0][1]*u.degree, dec=res[0][2]*u.degree)
            for i, key in enumerate(DBScheme[table]):
                if 'ascension' in key:
                    toinsert = c.ra.to_string('h')
                elif 'declination' in key:
                    toinsert = c.dec.to_string('deg')
                else:
                    toinsert = res[0][i]
                data.update({key: toinsert})
        else:
            for i in range(len(DBScheme[table])):
                data.update({DBScheme[table][i]: [j[i] for j in res]})
# Removing the star_id key, which is internal to the database and has no meaning outside
                data.pop('star_id', None)

    return data


def is_entry_valid(tableout, field, value):
    """
    This function will test that the arguments passed for database modification are correct.
    The number of arguments and their type is checked.
    If they mismatch, False is returned, and the database() function will not do anything.
    """
    if not isinstance(field, tuple) and not isinstance(value, tuple):
        return True
    if type(field) != type(value):
        print("Arguments for database modification mismatch")
        print(("type of field : {0} and type of value :{1}".format(type(field), type(value))))
        return False
    if isinstance(field, tuple):
        if len(field) != len(value):
            print("Number of parameters mismatch. Aborting.")
            return False
    # Checking if the fields are in the database.
    for key in DBScheme[tableout]:
        match_rows = [j for j in field if j in DBScheme[tableout]]
        if not match_rows:
            print("Field does not exist in the database.")
            return False
        if len(match_rows) != len(field):
            print("Some fields do not exist in the database")
            return False

    return True


def database(action, tableout, star, field, value, tablein='stars'):
    isvalid = is_entry_valid(tableout, field, value)
    if not isvalid:
        sys.exit()

    # Input is valid, let's proceed.

    if action == 'delete' or action == 'del':
        removeparameter(tablein, tableout, star, field, value)
    elif action == 'insert' or action == 'add':
        addparameter(tablein, tableout, star, field, value)
    elif action == 'update':
        print("update", star, field, value)
        update(star, field, value)
    else:
        print("Action should be : delete or insert. Or use the function list() to get all infos concerning one object.")


def removeparameter(tablein, tableout, star, field, value):
    id = getid(star)
    present, field, value = checkentry(tableout, field, id, value)
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
        if isinstance(field, str):
            test.update({row: AsIs(field)})
            test.update({val: value})
        if isinstance(field, tuple):
            test.update({row: AsIs(field[i])})
            test.update({val: AsIs(value[i])})

# query template
    SQL = "delete from %(table)s where " + query + " and  id = " + str(id)
    #print SQL, test
    # print (cursor.mogrify(SQL, test))
    # print present

    # present = True
    if present:
        print(("Deleting {0} in table {1} for star {2}".format(value, tableout, star)))
        # cursor.execute(" delete from %s where id=(%s) and %s = (%s)", (AsIs(tableout), id, AsIs(field), value))
        try:
            print(cursor.mogrify(SQL, test))
            #cursor.execute(SQL, test)
        except psycopg2.ProgrammingError as error:
            print(error.pgerror)
            print("Error, rolling back")
            connection.rollback()
    else:
        print(("Value {0} not in table {1} for star {2}".format(value, tableout, star)))
    connection.commit()


def addparameter(tablein, tableout, star, field, value):
    """ Add a parameter for a given star into the proper table

    """
# Get the ID of the star
    id = getid(star)[0][0]
    present, field, newvalue = checkentry(tableout, field, id, value)
    # print ("new values : ", present, field, value)
    # print

# Preparing the insert SQL query.
    if present is False:
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
            rows = rows + coma + " %("+row+")s"
            values = values + coma + " %("+val+")s"
            if isinstance(field, str):
                test.update({row: AsIs(field)})
                test.update({val: newvalue})
            if isinstance(field, tuple):
                test.update({row: AsIs(field[i])})
                test.update({val: AsIs(newvalue[i])})
        rows = "(star_id," + rows + ")"
        values = "(" + str(id) + "," + values + ")"
        #print rows
        #print values
        #print test
        query = "%(table)s " + rows + " values " + values

# query template
        SQL = "insert into " + query
    #print SQL
        #print(cursor.mogrify(SQL, test))
        cursor.execute(SQL, test)

    else:
        print(("Value {0} already in table {1} for star {2}".format(value, tableout, star)))
    connection.commit()


def flattenlist(list):
    # original code found here: http://stackoverflow.com/a/2158532
# This function unnests a list into a simple list
    for element in list:
        if isinstance(element, collections.Iterable) and not isinstance(element, str):
            for sub in flattenlist(element):
                yield sub
        else:
            yield element


def checkentry2():
    # Use the database properties to remove duplicates after insertion, rather than trying to prevent their insertion.
    pass


def checkentry(table, field, id, value):
    present = False
    print(("Checking input data: {0}, {1}, {2}".format(table, field, value)))
    SQL = "select %s from %s where star_id = %s"
    t1 = AsIs(table)
    if isinstance(field, str):
        f1 = [AsIs(field)]
    if isinstance(field, tuple):
        f1 = [AsIs(i) for i in field]
    data = (f1, t1, id)
    present = False
    try:
        #print cursor.mogrify(SQL, data)
        cursor.execute(SQL, data)
        result = cursor.fetchall()
# We check that the value to be insered is not here already.
        # print value, result
# Transforming the output and the input into lists.
        a = [i for i in flattenlist(result)]
        if isinstance(value, int) or isinstance(value, str):
            b = value
        else:
            b = [i for i in flattenlist(value)]
        #print "In : {0} and out :{1}".format(b, a)
        if isinstance(b, int) or isinstance(b, str):
            #print (a, b, field)
            if b in a:
                print("present")
                present = True
        if isinstance(b, list):
            # print type(a), type(b), type(field)
            f = [i for i in flattenlist(field)]
            #print a,b,f
            c = [i for i in a if i in b]
            for val in c:
                # We remove the duplicated values, and remove the corresponding field.
                f.remove(f[b.index(val)])
                b.remove(val)
            field = tuple(f)
            value = b
            #print("New values:", a,value,field)
            if not field:
                # Data already
                present = True

    except psycopg2.ProgrammingError as error:
        print(error.pgerror)
        print("Error, rolling back")
        connection.rollback()
    return present, field, value


def getid(star):
    # Penser `a verifier que l'étoile existe.

    cursor.execute("select id from stars where name = (%s)", (star,))
    res = cursor.fetchall()
    return res
