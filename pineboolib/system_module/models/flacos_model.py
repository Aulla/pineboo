# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flacos(BASE):
    __tablename__ = 'flacos'

# --- Metadata ---> 
    legacy_metadata = {'name' : 'flacos', 'alias' : 'Objetos de Control de Acceso', 
        'fields' : [
        {'name' : 'idaco', 'alias' : 'Identificador', 'pk' : True, 'type' : 'serial', 'null' : False, 'visiblegrid' : False},
        {'name' : 'nombre', 'alias' : 'Nombre', 'ck' : True, 'type' : 'string', 'length' : 100, 'null' : False},
        {'name' : 'permiso', 'alias' : 'Permiso', 'type' : 'string', 'length' : 50, 'regexp' : '[r-][w-]', 'null' : False, 'default' : '--'},
        {'name' : 'idac', 'alias' : 'Control de Acceso', 'ck' : True, 'type' : 'uint', 'relations' : [{'card' : 'M1', 'table' : 'flacs', 'field' : 'idac', 'delc' : True}], 'null' : False, 'visiblegrid' : False},
        {'name' : 'descripcion', 'alias' : 'Descripción', 'type' : 'string', 'length' : 100},
        {'name' : 'tipocontrol', 'alias' : 'Control', 'type' : 'string', 'length' : 30, 'default' : 'Todos', 'optionslist' : ['Botón', 'Campo', 'Tabla', 'Grupo de controles', 'Pestaña', 'Todos', ]}
        ]}

# <--- Metadata --- 


# --- Fields ---> 

    idaco = sqlalchemy.Column('idaco', sqlalchemy.Integer, primary_key = True)
    nombre = sqlalchemy.Column('nombre', sqlalchemy.String(100))
    permiso = sqlalchemy.Column('permiso', sqlalchemy.String(50))
    idac = sqlalchemy.Column('idac', sqlalchemy.BigInteger)
    descripcion = sqlalchemy.Column('descripcion', sqlalchemy.String(100))
    tipocontrol = sqlalchemy.Column('tipocontrol', sqlalchemy.String(30))

# <--- Fields --- 

