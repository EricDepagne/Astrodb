# -*- coding: utf-8 -*-
"""
An attempt to modelize datas with the "peewee" ORM and demonstrate it in a one shot script

You have to install "peewee" from its repository because this code use ManyToManyField that has been documented but omitted from the last release (so temporary waiting for it, we will develop using the unstable version): ::

    pip install -e git+https://github.com/coleifer/peewee#egg=peewee

Also, the code should be splitted in some modules and not resides anymore in the models.

"""
import os
import decimal, random

from peewee import *
from playhouse.shortcuts import ManyToManyField


# Uncomment this to see executed SQL queries from peewee ORM
import logging
logging.basicConfig(
    format='[%(asctime)-15s] [%(name)s] %(levelname)s]: %(message)s',
    level=logging.DEBUG
)


def decimal_round(value, decimal_places=2):
    """
    Rounds a number using the Decimal's quantize() method
    """
    q = decimal.Decimal((0, (1,), -decimal_places))
    return decimal.Decimal(value).quantize(q)


# Dummy connector using sqlite3 for demo, will have to do it using some user
# settings to use another database type
#database_filepath = 'my_app.db'
#db = SqliteDatabase(database_filepath)
#
database_filepath = 'AstroTest'
user = 'postgres'
host = 'localhost'
port = 5432

db = PostgresqlDatabase(database_filepath, user=user, host=host, port=port)


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

    What's a ManyToMany relation (or m2m relation) ?
    ************************************************

    ManyToMany means "Multiple object can relates on multiple object relations"

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


"""
Init db
"""
# Remove previous database file if any
print "=== Cleanup ==="
if os.path.exists(database_filepath):
    os.remove(database_filepath)
print

# Connecting to the database and create tables for models
print "=== Creating tables ==="
db.connect()
db.create_tables([Name, Star, StarName, Temperature, RadialVelocity, Abundance])
print


"""
Playing with Name model
"""
print "=== Creating a single Name objects ==="
print u"    └── Adding name: Meuh"
name = Name(name="Meuh")
name.save()
print

print "=== Creating some Name objects ==="
name_samples = (
    'Foo',
    'HD-551',
    u'Stérototo',
    'Sterotata',
    'Terminator',
    'Terminator-2',
    'Terminator-3',
    'Mojo',
    'Sveetch-42',
    'Tattoine',
    'Mars',
    'Lune',
    'Moon',
    'Esteban',
    'Esteban-1',
)
for item in name_samples:
    print u"    ├── Adding name:", item
    name = Name(name=item)
    name.save()

print u"    └── Total added objects", Name.select().count()
print

# Get an unique object
name_pattern = "Mojo"
print "# Getting a simple object with name='{0}':".format(name_pattern)
name_obj = Name.get(Name.name == name_pattern)
print ">>>", name_obj, name_obj.id, name_obj.name
print

# A dict to store selected item from their pattern, to use them further
name_store = {}

# Select multiple names
for name_pattern in ["Terminator", "Esteban", "Sterotata"]:
    print "# Getting all object with name starting with '{0}':".format(name_pattern)
    name_results = Name.select().where(Name.name.startswith(name_pattern))
    print ">>>", name_results.count()
    print ">>>", [item.name for item in name_results]
    name_store[name_pattern] = list(name_results)  # For interpretation of lazy query into python list
    print


"""
Playing with Star model
"""
print "=== Creating a single Star object ==="
print u"    └── Adding star: ra(0.10); dec(15.33); names(Foo);"
star = Star(right_ascension=0.10, declination=15.33)
star.save()
star.names.add(Name.get(Name.name == "Foo"))
print

print "=== Creating some Star objects ==="
for k, v in name_store.items():
    # Prepare some random floating values
    right_ascension = decimal_round(random.uniform(0, 42))
    declination = decimal_round(random.uniform(0, 42))

    names_render = ", ".join([item.name for item in v])
    print u"    └── Adding star: ra({ra}); dec({dec}); names({names});".format(ra=right_ascension, dec=declination, names=names_render)

    # Create the new star object
    star = Star(right_ascension=right_ascension, declination=declination)
    star.save()
    # Then add it some names (m2m field need the object id so we can only
    # add relations AFTER the object is created)
    for item in v:
        star.names.add(item)
    print u"        └── total names added :", star.names.select().count()

print
print "Finished!"
