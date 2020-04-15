# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flgroups(BASE):
    __tablename__ = 'flgroups'

# --- Metadata ---> 
    legacy_metadata = {'name' : 'flgroups', 'alias' : 'Grupos de Usuarios', 
        'fields' : [
        {'name' : 'idgroup', 'alias' : 'Nombre', 'pk' : True, 'type' : 'string', 'length' : 30, 'relations' : [{'card' : '1M', 'table' : 'flusers', 'field' : 'idgroup'}, {'card' : '1M', 'table' : 'flacs', 'field' : 'idgroup'}], 'null' : False},
        {'name' : 'descripcion', 'alias' : 'Descripción', 'type' : 'string', 'length' : 100}
        ]}

# <--- Metadata --- 


# --- Fields ---> 

    idgroup = sqlalchemy.Column('idgroup', sqlalchemy.String(30), primary_key = True)
    descripcion = sqlalchemy.Column('descripcion', sqlalchemy.String(100))

# <--- Fields --- 

