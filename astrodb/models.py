"""
An attempt to modelize datas with the "peewee" ORM

You have to install "peewee" from its repository (this code use ManyToManyField that has been documented but omitted from the last release, so waiting for it we will develop using the unstable version): ::

    pip install -e git+https://github.com/coleifer/peewee#egg=peewee

For now this is a one shot script, implying you have to remove the database file before re-run it.

Also, the code should be splitted in some modules and not resides anymore in the models.
"""
import os

from peewee import *
from playhouse.shortcuts import ManyToManyField

# Dummy connector using sqlite3 for demo, will have to do it using some user 
# settings to use another database type
database_filepath = 'my_app.db'
db = SqliteDatabase(database_filepath)

class BaseModel(Model):
    class Meta:
        database = db


class Name(BaseModel):
    """
    Name entry for stars
    """
    name = CharField(max_length=50, unique=True, null=False)

class Star(BaseModel):
    """
    Star model
    
    Can have multiple names that are not unique (Many stars can share the same names), so we use a ManyToMany relation
    """
    names = ManyToManyField(Name, related_name='stars')
    right_ascension = DoubleField(default=0.0, null=False)
    declination = DoubleField(default=0.0, null=False)

# Automatic through model for m2m (Many To Many) "name" relation 
StarName = Star.names.get_through_model()


class Temperature(BaseModel):
    """
    Temperature model
    """
    value = IntegerField(null=False)


class RadialVelocity(BaseModel):
    """
    Radial velocity model
    """
    value = DoubleField(default=0.0, null=False)
    observationdate = DoubleField(default=0.0, null=False)


class Abundance(BaseModel):
    """
    Abondance model
    """
    value = DoubleField(default=0.0, null=False)
    carbon = DoubleField(default=0.0, null=False)
    oxygen = DoubleField(default=0.0, null=False)


# Connecting to the database and create tables if not allready exists
if not os.path.exists(database_filepath):
    print "=== Creating tables ==="
    db.connect()
    db.create_tables([Name, Star, StarName, Temperature, RadialVelocity, Abundance])
    
print "Finished!"