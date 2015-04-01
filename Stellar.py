from peewee import *
import base64
import configparser

# Reading the configuration file
Config = configparser.ConfigParser()
Config.read('/home/eric/Science/Projets/Database/AstroConfig')
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
    name = CharField(null=True)
    pmdec = FloatField(db_column='pmDEC')
    pmra = FloatField(db_column='pmRA')
    right_ascension = FloatField(null=True)

    class Meta:
        db_table = 'Star'


class Gravity(BaseModel):
    gravity = FloatField(index=True)
    idgravity = PrimaryKeyField(db_column='idGravity')
    starid = ForeignKeyField(db_column='starid', rel_model=Star, to_field='idstar')

    class Meta:
        db_table = 'Gravity'


class Magnitude(BaseModel):
    b = FloatField()
    h = IntegerField()
    i = IntegerField()
    idmagnitude = PrimaryKeyField(db_column='idMagnitude')
    j = IntegerField()
    k = IntegerField()
    r = IntegerField()
    starid = ForeignKeyField(db_column='starid', rel_model=Star, to_field='idstar')
    u = FloatField()
    v = IntegerField()

    class Meta:
        db_table = 'Magnitude'


class Name(BaseModel):
    alternatename = CharField(index=True)
    idname = PrimaryKeyField(db_column='idName')
    starid = ForeignKeyField(db_column='starid', rel_model=Star, to_field='idstar')

    class Meta:
        db_table = 'Name'


class Temperature(BaseModel):
    idtemperature = PrimaryKeyField(db_column='idTemperature')
    starid = ForeignKeyField(db_column='starid', rel_model=Star, to_field='idstar')
    temperature = IntegerField()

    class Meta:
        db_table = 'Temperature'