# -*- coding: utf-8 -*-
"""
Some stuff to query the database
"""
# System imports
import base64
import configparser
import os
import sys
# peewee imports
from peewee import Model, MySQLDatabase
from peewee import FloatField, CharField, PrimaryKeyField, IntegerField, ForeignKeyField, DecimalField

# Reading the configuration file
Config = configparser.ConfigParser()

configfile = os.path.expanduser("~") + '/.Astro/config'
if os.path.isfile(configfile):
    Config.read(configfile)
else:
    print('A MySQL configuration file is required. The file should be located be ~/Astro/config . For safety reasons, it should have as little permissions as possible. The file should be in the INI format, with a MySQL section that contains the username and password of the user that will connect to the database')
    sys.exit(0)
user = Config.get('MySQL', 'user')
password = base64.encodebytes(bytes(Config.get('MySQL', 'passwd'), "utf-8"))

database = MySQLDatabase('Stellar', **{'password': base64.decodebytes(password).decode(), 'user': user})
# deleting the password.

del password


class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class Star(BaseModel):
    declination = FloatField(null=True)
    epoch = CharField(null=True)
    idstar = PrimaryKeyField(db_column='idStar')
    name = CharField(unique=True)
    pmdec = FloatField(db_column='pmDEC', null=True)
    pmra = FloatField(db_column='pmRA', null=True)
    rightascension = FloatField(null=True)

    class Meta:
        db_table = 'Star'

class Abundance(BaseModel):
    carbon = FloatField(db_column='Carbon', null=True)
    oxygen = FloatField(db_column='Oxygen', null=True)
    titanium = FloatField(db_column='Titanium', null=True)
    idabundance = PrimaryKeyField(db_column='idAbundance')
    starid = ForeignKeyField(db_column='starid', rel_model=Star, to_field='idstar')

    class Meta:
        db_table = 'Abundance'

class Dimension(BaseModel):
    iddimension = PrimaryKeyField(db_column='idDimension')
    mass = FloatField()
    radius = FloatField()
    starid = ForeignKeyField(db_column='starid', rel_model=Star, to_field='idstar')

    class Meta:
        db_table = 'Dimension'

class Frequency(BaseModel):
    deltanu = FloatField()
    idfrequency = PrimaryKeyField(db_column='idFrequency')
    numax = FloatField()
    starid = ForeignKeyField(db_column='starid', rel_model=Star, to_field='idstar')

    class Meta:
        db_table = 'Frequency'

class Gravity(BaseModel):
    gravity = FloatField(index=True)
    idgravity = PrimaryKeyField(db_column='idGravity')
    starid = ForeignKeyField(db_column='starid', rel_model=Star, to_field='idstar')

    class Meta:
        db_table = 'Gravity'

class Magnitude(BaseModel):
    bmag = DecimalField()
    hmag = DecimalField()
    idmagnitude = PrimaryKeyField(db_column='idMagnitude')
    imag = DecimalField()
    jmag = DecimalField()
    kmag = DecimalField()
    rmag = DecimalField()
    starid = ForeignKeyField(db_column='starid', rel_model=Star, to_field='idstar')
    umag = DecimalField()
    vmag = DecimalField()

    class Meta:
        db_table = 'Magnitude'

class Name(BaseModel):
    alternatename = CharField(index=True)
    idname = PrimaryKeyField(db_column='idName')
    starid = ForeignKeyField(db_column='starid', rel_model=Star, to_field='idstar')

    class Meta:
        db_table = 'Name'

class Temperature(BaseModel):
    deltat = IntegerField(db_column='deltaT')
    idtemperature = PrimaryKeyField(db_column='idTemperature')
    starid = ForeignKeyField(db_column='starid', rel_model=Star, to_field='idstar')
    temperature = IntegerField()

    class Meta:
        db_table = 'Temperature'
