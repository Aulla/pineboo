# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flusers(BASE):
    __tablename__ = 'flusers'

# --- Metadata ---> 
    legacy_metadata = {'name' : 'flusers', 'alias' : 'Usuarios', 
        'fields' : [
        {'name' : 'iduser', 'alias' : 'Nombre', 'pk' : True, 'type' : 'string', 'length' : 30, 'relations' : [{'card' : '1M', 'table' : 'flacs', 'field' : 'iduser'}], 'null' : False},
        {'name' : 'idgroup', 'alias' : 'Grupo', 'type' : 'string', 'length' : 30, 'null' : False},
        {'name' : 'descripcion', 'alias' : 'Descripción', 'type' : 'string', 'length' : 100}
        ]}

# <--- Metadata --- 


# --- Fields ---> 

    iduser = sqlalchemy.Column('iduser', sqlalchemy.String(30), primary_key = True)
    idgroup = sqlalchemy.Column('idgroup', sqlalchemy.String(30))
    descripcion = sqlalchemy.Column('descripcion', sqlalchemy.String(100))

# <--- Fields --- 

