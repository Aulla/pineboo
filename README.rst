.. image:: https://gitlab.com/aulla/pineboo/badges/master/pipeline.svg
    :target: https://gitlab.com/aulla/pineboo/commits/master
    :alt: pipeline status

.. image:: https://gitlab.com/aulla/pineboo/badges/master/coverage.svg
    :target: https://gitlab.com/aulla/pineboo/commits/master
    :alt: coverage report

Pineboo - Manual de supervivencia
===================================
Se ha redactado este manual para las dudas más comunes sobre este proyecto de
investigación, y ayudar a que cualquiera pueda poner en marcha y realizar las
pruebas que desee con el mismo.

¿Qué demonios es Pineboo?
----------------------------
Pineboo es un proyecto de investigación, donde no se pretende obtener un producto
final, sino sentar una base y crear las tecnologías necesarias para el día de mañana
crear realmente el/los producto(s) que se deseen.

Lo que se desea es contestar a la frase: "Qué necesitamos para poder ejecutar un proyecto
de módulos de Eneboo sin Eneboo?"

Para ello, se crea un micro-proyecto (o mejor dicho, pico-proyecto) que solo cubre
lo mínimo necesario para cumplir esa frase, y estrictamente esa frase.

Es posible que exista más de una versión de Pineboo, cada una con distintas aproximaciones
y tecnologías. Actualmente, en el momento de escribir esta documentación, solo existe una.

El nombre de Pineboo viene de Pico-eneboo, y hace referencia que es un proyecto de
investigación


Aproximaciones existentes
---------------------------
Solo existe una única aproximación a la ejecución de proyectos de Eneboo:

 - Python3.x + PyQt6
 - Permite ejecutarlo en PostgreSQL, SQLite ,MySQL y MSSQL.
 - Motor realizado integramente en Python
 - Conversión al vuelo de QSA a PY con parseador FLScriptParser2
 - Conversión al vuelo de formularios Qt3 a Qt4 creando un UiLoader manualmente
 - Conversión al vuelo de fichero .mtd a modelos sqlAlchemy
 - Conversión al vuelo de fichros .kut a pdf


Dependencias
----------------
 - Python >= 3.8
 - PyQt6 >= 6.0.3
 - PsycoPG2

Alcance actual de Pineboo
---------------------------
Pineboo es capaz de conectarse a cualquier base de datos de Eneboo y realizar
las siguientes tareas:

 - Funcionamientos habituales de las acciones
 - Trabajos normales de cursor (afterCommit, beforeCommit, ...)
 - Transacciones plenamente operativas sobre postgres
 - Impresión con jasperPluging configurado


Al iniciar una acción, el formulario es convertido al vuelo a Qt4 (con errores) y
el script QS es convertido a Python y ejecutado (con muchos más errores). Se
lanza el init() automáticamente.

Las referencias entre módulos (flfacturac.iface.XYZ) funcionan con carga de módulo
retrasada.

La API de QSA y Eneboo está practicamente terminada. En la API aún existente son
funciones y clases "fake", que desde el script, parece que funcionen pero no
realizan ningún trabajo. Esto permite ejecutar los scripts, pero no opera correctamente.

¿Si cargo Pineboo en mi base de datos de producción, puedo perder datos?
-------------------------------------------------------------------------
Sí, pueden perderse datos. Los experimentos con gaseosa.

Dado que es un motor experimental, puede que no realice el trabajo que se le
mande, sino otro inesperado. Un script podría de forma inadvertida borrar registros
por fallos en la API implementada. Y aquí nadie se hace responsable de esto.

Lo mejor es usarlo en bases de datos de desarrollo para evitar problemas.


Cómo poner en marcha Pineboo
------------------------------

1) Instalar desde apt-get.

sudo apt-get install python3-pip git libmysqlclient-dev

2) Actualizar pip.

sudo -H pip3 install --upgrade pip

3) Descargamos pineboo

sudo -H pip3 install pineboo


Al llamar al programa Pineboo éste crea el subdirectorio "/profiles".

Desde ese formulario se configura el acceso a la empresa elegida



Con esto, pineboo debería iniciarse así::

    pineboo

Cosas que se pueden probar en Pineboo
----------------------------------------
La opción --help ofrece un listado de opciones, algunas pueden ser interesantes.

Los formularios con convertidos al vuelo, y aún requiere este proceso de muchos
retoques. Las características más usadas funcionan, pero muchas de las cosas
que se pueden hacer en un formulario de Eneboo aún no son intepretadas correctamente.

Para ejecutar los scripts se usan tres capas de compatibilidad: flcontrols, qsaglobals
y qsatypes.

Los ficheros son convertidos a python y guardados junto al fichero QS de cache.
Por ejemplo, las conversiones de masterarticulos.qs se pueden ver en la ruta
`tempdata/cache/nombre_bd/flfactalma/file.qs/masterarticulos/`.
