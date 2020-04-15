# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flvar(BASE):
    __tablename__ = 'flvar'

# --- Metadata ---> 
    legacy_metadata = {'name' : 'flvar', 'alias' : 'Variables', 
        'fields' : [
        {'name' : 'id', 'alias' : 'Identificador', 'pk' : True, 'type' : 'serial', 'null' : False, 'visiblegrid' : False},
        {'name' : 'idvar', 'alias' : 'Identificador de la variable', 'ck' : True, 'type' : 'string', 'length' : 30, 'null' : False},
        {'name' : 'idsesion', 'alias' : 'Identificador de la sesión', 'ck' : True, 'type' : 'string', 'length' : 30, 'null' : False},
        {'name' : 'valor', 'alias' : 'Valor', 'type' : 'stringlist', 'null' : False, 'visiblegrid' : False}
        ]}

# <--- Metadata --- 


# --- Fields ---> 

    id = sqlalchemy.Column('id', sqlalchemy.Integer, primary_key = True)
    idvar = sqlalchemy.Column('idvar', sqlalchemy.String(30))
    idsesion = sqlalchemy.Column('idsesion', sqlalchemy.String(30))
    valor = sqlalchemy.Column('valor', sqlalchemy.String)

# <--- Fields --- 

