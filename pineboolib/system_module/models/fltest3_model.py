# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Fltest3(BASE):
    __tablename__ = 'fltest3'

# --- Metadata ---> 
    legacy_metadata = {'name' : 'fltest3', 'alias' : 'Test table', 
        'fields' : [
        {'name' : 'counter', 'alias' : 'Contador', 'pk' : True, 'type' : 'string', 'length' : 6, 'null' : False, 'counter' : True, 'visiblegrid' : False, 'editable' : False},
        {'name' : 'string_field', 'alias' : 'String field', 'type' : 'string'},
        {'name' : 'timezone_field', 'alias' : 'TimeZone field', 'type' : 'timestamp', 'null' : False},
        {'name' : 'bool_field', 'alias' : 'Bool field', 'type' : 'bool', 'null' : False}
        ]}

# <--- Metadata --- 


# --- Fields ---> 

    counter = sqlalchemy.Column('counter', sqlalchemy.String(6), primary_key = True)
    string_field = sqlalchemy.Column('string_field', sqlalchemy.String)
    timezone_field = sqlalchemy.Column('timezone_field', sqlalchemy.DateTime)
    bool_field = sqlalchemy.Column('bool_field', sqlalchemy.Boolean)

# <--- Fields --- 

