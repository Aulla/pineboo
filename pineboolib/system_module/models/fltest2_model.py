# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Fltest2(BASE):
    __tablename__ = 'fltest2'

# --- Metadata ---> 
    legacy_metadata = {'name' : 'fltest2', 'alias' : 'Test table', 'query':'fltest2', 
        'fields' : [
        {'name' : 'id', 'alias' : 'ID', 'pk' : True, 'type' : 'serial', 'null' : False, 'visiblegrid' : False, 'editable' : False},
        {'name' : 'string_field', 'alias' : 'String field', 'type' : 'string'},
        {'name' : 'date_field', 'alias' : 'Date field', 'type' : 'date'},
        {'name' : 'time_field', 'alias' : 'Time field', 'type' : 'time'},
        {'name' : 'double_field', 'alias' : 'Double field', 'type' : 'double', 'default' : '0', 'partI' : 6, 'partD' : 2},
        {'name' : 'bool_field', 'alias' : 'Bool field', 'type' : 'bool'},
        {'name' : 'uint_field', 'alias' : 'Unsigned int field', 'type' : 'uint', 'default' : '0'},
        {'name' : 'int_field', 'alias' : 'Int field', 'type' : 'int', 'default' : '0'},
        {'name' : 'bloqueo', 'alias' : 'Bloqueo', 'type' : 'unlock', 'null' : False, 'default' : 'True'}
        ]}

# <--- Metadata --- 


# --- Fields ---> 

    id = sqlalchemy.Column('id', sqlalchemy.Integer, primary_key = True)
    string_field = sqlalchemy.Column('string_field', sqlalchemy.String)
    date_field = sqlalchemy.Column('date_field', sqlalchemy.DateTime)
    time_field = sqlalchemy.Column('time_field', sqlalchemy.DateTime)
    double_field = sqlalchemy.Column('double_field', sqlalchemy.Numeric(6 , 2))
    bool_field = sqlalchemy.Column('bool_field', sqlalchemy.Boolean)
    uint_field = sqlalchemy.Column('uint_field', sqlalchemy.BigInteger)
    int_field = sqlalchemy.Column('int_field', sqlalchemy.Integer)
    bloqueo = sqlalchemy.Column('bloqueo', sqlalchemy.Boolean)

# <--- Fields --- 

