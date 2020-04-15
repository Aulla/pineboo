# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flsettings(BASE):
    __tablename__ = 'flsettings'

# --- Metadata ---> 
    legacy_metadata = {'name' : 'flsettings', 'alias' : 'Configuración global', 
        'fields' : [
        {'name' : 'flkey', 'alias' : 'Clave', 'pk' : True, 'type' : 'string', 'length' : 30, 'null' : False},
        {'name' : 'valor', 'alias' : 'Valor', 'type' : 'stringlist', 'visiblegrid' : False}
        ]}

# <--- Metadata --- 


# --- Fields ---> 

    flkey = sqlalchemy.Column('flkey', sqlalchemy.String(30), primary_key = True)
    valor = sqlalchemy.Column('valor', sqlalchemy.String)

# <--- Fields --- 

