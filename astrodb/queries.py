# -*- coding: utf-8 -*-
"""
Some stuff to query and populate the database
"""
# python imports
# import decimal

# Scientific  imports
import numpy as np
import pandas as pd
from decimal import Decimal
from decimal import getcontext

# Astronomical imports
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astropy.table import Column
from astropy import units as u

# peewee imports
from peewee import IntegrityError
# Stellar imports
from Stellar import Star, Gravity, Magnitude, Name, Temperature, Abundance

# Setting the precision of the decimal objects
getcontext().prec = 3
# Star is the main table of the database. All other tables are directly linked to it. Knowing the full content of the DB requires listing the content of Star.

Database = {'Temperature': ['starid', 'temperature'],
            'Gravity': ['starid', 'gravity'],
            'Name': ['starid', 'alternatename'],
            'Abundance': ['starid', 'Carbon', 'Oxygen', 'Titanium'],
            'Magnitude': ['starid', 'umag', 'bmag', 'vmag', 'rmag', 'imag', 'jmag', 'hmag', 'kmag'],
            'Star': ['idstar', 'name', 'rightascension', 'declination', 'pmra', 'pmdec']}

# The default parameters for a simbad query do not contain enough fields for our needs.
# Missing are magnitudes, proper motions, metallicities
# Let's add them now.
Filters = ['U', 'B', 'V', 'R', 'I', 'J', 'H', 'K']
Motions = ['pmra', 'pmdec']

fields = Simbad.get_votable_fields()
print(fields)
Present = False
for f in fields:
    if 'flux' in f:
        Present = True

if not Present:
    for Filter in Filters:
        Simbad.add_votable_fields('flux('+Filter+')')

fields = Simbad.get_votable_fields()
Present = False
for f in fields:
    if 'pm'in f:
        Present = True
if not Present:
    for Motion in Motions:
        Simbad.add_votable_fields(Motion)


def query(star):
    n = Simbad.query_objectids(star)
    d = Simbad.query_object(star)
# Simbad returns bytecode. Changing it to strings.
    n.convert_bytestring_to_unicode()
# Transforming the n Astropy NameTable into a string, so we can insert it in a DataFrame cell directly.
    t = ', '.join([i for i in n['ID']])
# Adding a column with the alternate names.
    d['ALTNAME'] = Column([t], dtype=object)
    return d


def correctname(star):
    """
    Modify the name of some stars so it matches the simbad naming scheme
    """
    # Correction for the BPS stars.
    if star.startswith('BS') or star.startswith('CS'):
        star = 'BPS ' + star
    #
    return star


def onlinedata(star):
    """
    Query the Simbad database to get the information about the star(s)(s).
    """
    data = None
    if not isinstance(star, list):
        star = [star]
    for s in star:
        # Stacking the results one after each in a numpy array.
        s = correctname(s)
        print('Star : {0}'.format(s))
        d = query(s)
        if data is None:
            data = np.array(d)
        else:
            data = np.hstack((data, d))
    df = pd.DataFrame(data)
# Coordinates are stored in the databse as Decimal() objects, so we transform them into a decimal.
# We use astropy SkyCoords objects to do so.
    # coords = SkyCoord(ra=df['RA'], dec=df['DEC'], unit=(u.hourangle, u.deg))
#    for i in range(df.shape[0]):
#        ra = df['RA'][i]
#        dec = df['DEC'][i]
#        sc = SkyCoord(ra=ra, dec=dec, unit=(u.hourangle, u.deg))
#        df.loc[i:i, ('RA')] = decimalformat(sc.ra.hour)
#        df.loc[i:i, ('DEC')] = decimalformat(sc.dec.deg)

    return df


def decimalformat(value):
    """
    Allows the Decimal numbers to have the proper format
    """
    getcontext().prec = 8
    v = str(value)
    return Decimal(v)/Decimal('1.000000')


def listofstars():
    """
    Returns a list of all the stars present in the Star table
    """
    a = []
    for star in Star.select():
        a.append(star.name)
    return a


def addstar(starname):
    """
    Add a record in the database.
    """
    try:
        Star.create(name=starname)
    except IntegrityError:
        print('Star {0} already in database. Record not created, but can be updated.'.format(starname))


def addinfostar(star, field, value):
    id = idstar(star)
    for table, attribute in Database.items():
        if field in attribute:
            model = table
    toinsert = {'starid': id,
                field: value}
    print('Inserting {0} into {1}:{2} for star {3}'.format(value, model, field, star))
    toi = eval(model)(**toinsert)
    return toi.save()


def idstar(star):
    # query = Gravity.select().where(Gravity.gravity != 0)
    # for g in query:
    #     ...:     print (g.gravity, g.starid.name, g.starid.pmra)
    # In this case, since the table Gravity is linked to the table Star via starid, we get the name of the star directly using starid.name
    """
    Returns the data for a given star.
    """
    # Star._meta.columns lists all columns of the Table.
    # Gravity._meta.database.get_tables() liste toutes les tables de la base de données
    id = Star.get(Star.name == star).get_id()

    return id


def getdata(star):
    if isinstance(star, list):
        result = {}
        for s in star:
            result.update({s: extractdata(idstar(s))})
        return result
    elif isinstance(star, str):
        return(extractdata(idstar(star)))
    else:
        return


def extractdata(id):
    temp = {}
# Getting the parameters from the tables.
    for key in Database.keys():
        val = {}
        for attr in Database[key]:
            params = []
            if attr == 'starid' or attr == 'idstar':
                continue
            if key == 'Star':
                query = Star.select().where(Star.idstar == id)
            else:
                query = eval(key).select().join(Star).where(Star.idstar == id)
            for field in query:
                if attr != 'starid':
                    params.append(getattr(field, attr))
                val.update({attr: params})
        if val:
            temp.update(val)
    return temp
