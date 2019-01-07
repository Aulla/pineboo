from PyQt5.Qt import qWarning, QApplication
from PyQt5.QtWidgets import QMessageBox

from pineboolib.utils import auto_qt_translate_text, checkDependencies

from pineboolib.utils import text2bool
from pineboolib.fllegacy.flsqlquery import FLSqlQuery
from pineboolib.fllegacy.flutil import FLUtil
import pineboolib

import sys
import traceback



class FLMYSQL_MYISAM(object):

    version_ = None
    conn_ = None
    name_ = None
    alias_ = None
    errorList = None
    lastError_ = None
    cursorsArray_ = None
    noInnoDB = None
    mobile_ = False
    pure_python_ = False
    defaultPort_ = None
    cursor_ = None

    def __init__(self):
        self.version_ = "0.6"
        self.conn_ = None
        self.name_ = "FLMYSQL_MyISAM"
        self.open_ = False
        self.errorList = []
        self.alias_ = "MySQL_MyISAM"
        self.cursorsArray_ = {}
        self.noInnoDB = True
        self._dbname = None
        self.mobile_ = False
        self.pure_python_ = False
        self.defaultPort_ = 3306
        self.rowsFetched = {}

    def version(self):
        return self.version_

    def driverName(self):
        return self.name_

    def pure_python(self):
        return self.pure_python_

    def safe_load(self):
        return checkDependencies({"MySQLdb": "mysqlclient"}, False)

    def mobile(self):
        return self.mobile_

    def isOpen(self):
        return self.open_

    def DBName(self):
        return self._dbname

    def connect(self, db_name, db_host, db_port, db_userName, db_password):
        self._dbname = db_name
        checkDependencies({"MySQLdb": "mysqlclient"})
        import MySQLdb

        try:
            self.conn_ = MySQLdb.connect(db_host, db_userName, db_password, db_name)
        except MySQLdb.OperationalError as e:
            pineboolib.project._splash.hide()
            if "Unknown database" in str(e):
                ret = QMessageBox.warning(None, "Pineboo",
                                          "La base de datos %s no existe.\n¿Desea crearla?" % db_name,
                                          QMessageBox.Ok | QMessageBox.No)
                if ret == QMessageBox.No:
                    return False
                else:
                    try:
                        tmpConn = MySQLdb.connect(db_host, db_userName, db_password)
                        cursor = tmpConn.cursor()
                        try:
                            cursor.execute("CREATE DATABASE %s" % db_name)
                        except Exception:
                            print("ERROR: FLPSQL.connect",traceback.format_exc())
                            cursor.execute("ROLLBACK")
                            cursor.close()
                            return False
                        cursor.close()
                        return self.connect(db_name, db_host, db_port, db_userName, db_password)
                    except Exception:
                        qWarning(traceback.format_exc())
                        QMessageBox.information(
                            None, "Pineboo", "ERROR: No se ha podido crear la Base de Datos %s" % db_name, QMessageBox.Ok)
                        print(
                            "ERROR: No se ha podido crear la Base de Datos %s" % db_name)
                        return False
            
            
            else:
                QMessageBox.information(
                    None, "Pineboo", "Error de conexión\n%s" % str(e), QMessageBox.Ok)
                return False

        if self.conn_:
            self.open_ = True
            self.conn_.autocommit(True)
            self.conn_.set_character_set('utf8')

        return self.conn_
    
    def cursor(self):
        if not self.cursor_:
            self.cursor_ = self.conn_.cursor()
            #self.cursor_.execute('SET NAMES utf8;')
            #self.cursor_.execute('SET CHARACTER SET utf8;')
            #self.cursor_.execute('SET character_set_connection=utf8;')
        return self.cursor_

    def formatValueLike(self, type_, v, upper):
        res = "IS NULL"

        if type_ == "bool":
            s = str(v[0]).upper()
            if s == str(QApplication.tr("Sí")[0]).upper():
                res = "=1"
            elif str(QApplication.tr("No")[0]).upper():
                res = "=0"

        elif type_ == "date":
            util = FLUtil()
            res = "LIKE '%%" + util.dateDMAtoAMD(str(v)) + "'"

        elif type_ == "time":
            t = v.toTime()
            res = "LIKE '" + t.toString(QtCore.Qt.ISODate) + "%%'"

        else:
            res = str(v)
            if upper:
                res = "%s" % res.upper()

            res = "LIKE '" + res + "%%'"

        return res

    def formatValue(self, type_, v, upper):

        util = FLUtil()

        s = None

        # if v == None:
        #    v = ""
        # TODO: psycopg2.mogrify ???

        if v is None:
            s = "Null"

        elif type_ == "bool" or type_ == "unlock":
            s = text2bool(v)

        elif type_ == "date":
            #val = util.dateDMAtoAMD(v)
            val = v
            if val is None:
                s = "Null"
            else:
                s = "'%s'" % val

        elif type_ == "time":
            s = "'%s'" % v

        elif type_ in ("uint", "int", "double", "serial"):
            s = v

        elif type_ in ("string", "stringlist"):
            if v == "":
                s = "Null"
            else:
                if type_ == "string":
                    v = auto_qt_translate_text(v)
                if upper and type_ == "string":
                    v = v.upper()

                s = "'%s'" % v

        elif type_ == "pixmap":
            if v.find("'") > -1:
                v = self.normalizeValue(v)
            s = "'%s'" % v

        else:
            s = v
        # print ("PNSqlDriver(%s).formatValue(%s, %s) = %s" % (self.name_, type_, v, s))
        return s

    def canOverPartition(self):
        return True
    
    
    def tables(self, type_name=None):
        tl = []
        if not self.isOpen():
            return tl
        
        q_tables = FLSqlQuery()
        q_tables.exec_("show tables")
        while q_tables.next():
            tl.append(q_tables.value(0))
        
        return tl

            
            
    

    def nextSerialVal(self, table, field):
        if not self.isOpen():
            qWarning("%s::beginTransaction: Database not open" % self.name_)
            return None

        if not self.noInnoDB and self.transaction():
            self.setLastError(
                "No se puede iniciar la transacción", "BEGIN WORK")
            return None

        res = None
        row = None
        max = 0
        cur_max = 0
        updateQry = False
        ret = None
        
        q = FLSqlQuery()
        q.setSelect("max(%s)" % field)
        q.setFrom(table)
        q.setWhere("1 = 1")
        if not q.exec_():
            self.logger.warn("not exec sequence")
            return None
        if q.first() and q.value(0) is not None:
            max = q.value(0)

        cursor = self.conn_.cursor()



        #print(1,"max de %s.%s = %s" % (table, field, max))


        strQry = "SELECT seq FROM flseqs WHERE tabla = '%s' AND campo ='%s'" % (table, field)
        try:
            cur_max = cursor.execute(strQry)
        except Exception:
            qWarning("%s:: La consulta a la base de datos ha fallado" % (self.name_, traceback.format_exc()))
            self.rollbackTransaction()
            return
        
        
        #print(2,"cur_max de %s.%s = %s" % (table, field , cur_max))
        
        updateQry = cur_max > 0

        strQry = None
        ret = max + 1
        if updateQry:
            if ret > cur_max:
                strQry = "UPDATE flseqs SET seq=%s WHERE tabla = '%s' AND campo = '%s'" % (ret, table, field)
        else:
            strQry = "INSERT INTO flseqs (tabla,campo,seq) VALUES('%s','%s',%s)" % (table, field, ret)
        
        result = None
        
        if strQry is not None:
            try:
                result = cursor.execute(strQry)
            except Exception:
                qWarning("%s:: La consulta a la base de datos ha fallado\n %s" % (self.name_, traceback.format_exc()))
                if not self.noInnoDB:
                    self.rollbackTransaction()

                return


        if not self.noInnoDB and self.commitTransaction():
            qWarning("%s:: No se puede aceptar la transacción" % self.name_)
            return

        return ret
    
    def queryUpdate(self, name, update, filter):
        sql = "UPDATE %s SET %s WHERE %s" % (name, update, filter)
        return sql

    def savePoint(self, n):
        if not self.isOpen():
            qWarning("%s::savePoint: Database not open" % self.name_)
            return False

        cursor = self.cursor()
        try:
            cursor.execute("SAVEPOINT sv_%s" % n)
        except Exception:
            self.setLastError(
                "No se pudo crear punto de salvaguarda", "SAVEPOINT sv_%s" % n)
            qWarning("MySQLDriver:: No se pudo crear punto de salvaguarda SAVEPOINT sv_%s \n %s " % (
                n, traceback.format_exc()))
            return False

        return True

    def canSavePoint(self):
        return True

    def rollbackSavePoint(self, n):
        if not self.isOpen():
            qWarning("%s::rollbackSavePoint: Database not open" % self.name_)
            return False

        cursor = self.cursor()
        try:
            cursor.execute("ROLLBACK TO SAVEPOINT sv_%s" % n)
        except Exception:
            self.setLastError(
                "No se pudo rollback a punto de salvaguarda", "ROLLBACK TO SAVEPOINTt sv_%s" % n)
            qWarning("%s:: No se pudo rollback a punto de salvaguarda ROLLBACK TO SAVEPOINT sv_%s\n %s" % (
                self.name_, n, traceback.format_exc()))
            return False

        return True

    def setLastError(self, text, command):
        self.lastError_ = "%s (%s)" % (text, command)

    def lastError(self):
        return self.lastError_

    def commitTransaction(self):
        if not self.isOpen():
            qWarning("%s::commitTransaction: Database not open" % self.name_)

        cursor = self.cursor()
        try:
            cursor.execute("COMMIT")
        except Exception:
            self.setLastError("No se pudo aceptar la transacción", "COMMIT")
            qWarning("%s:: No se pudo aceptar la transacción COMMIT\n %s" %
                     (self.name_, traceback.format_exc()))
            return False

        return True

    def rollbackTransaction(self):
        if not self.isOpen():
            qWarning("%s::rollbackTransaction: Database not open" % self.name_)

        cursor = self.cursor()
        try:
            cursor.execute("ROLLBACK")
        except Exception:
            self.setLastError("No se pudo deshacer la transacción", "ROLLBACK")
            qWarning("%s:: No se pudo deshacer la transacción ROLLBACK\n %s" % (
                self.name_, traceback.format_exc()))
            return False

        return True

    def transaction(self):
        if not self.isOpen():
            qWarning("%s::transaction: Database not open" % self.name_)

        cursor = self.cursor()
        try:
            cursor.execute("START TRANSACTION")
        except Exception:
            self.setLastError("No se pudo crear la transacción", "BEGIN WORK")
            qWarning("%s:: No se pudo crear la transacción BEGIN\n %s" %
                     (self.name_, traceback.format_exc()))
            return False

        return True

    def releaseSavePoint(self, n):

        if not self.isOpen():
            qWarning("%s::releaseSavePoint: Database not open" % self.name_)
            return False

        cursor = self.cursor()
        try:
            cursor.execute("RELEASE SAVEPOINT sv_%s" % n)
        except Exception:
            self.setLastError(
                "No se pudo release a punto de salvaguarda", "RELEASE SAVEPOINT sv_%s" % n)
            qWarning("MySQLDriver:: No se pudo release a punto de salvaguarda RELEASE SAVEPOINT sv_%s\n %s" % (
                n, traceback.format_exc()))

            return False

        return True

    def setType(self, type_, leng=None):
        if leng:
            return "::%s(%s)" % (type_, leng)
        else:
            return "::%s" % type_

    def refreshQuery(self, curname, fields, table, where, cursor, conn):
        if curname not in self.cursorsArray_.keys():
            self.cursorsArray_[curname] = cursor

        sql = "SELECT %s FROM %s WHERE %s " % (fields, table, where)
        try:
            self.cursorsArray_[curname].execute(sql)
        except Exception:
            qWarning("CursorTableModel.Refresh\n %s" % traceback.format_exc())

    def refreshFetch(self, number, curname, table, cursor, fields, where_filter):
        try:
            self.cursorsArray_[curname].fetchmany(number)
        except Exception:
            qWarning("%s.refreshFetch\n %s" %(self.name_, traceback.format_exc()))

    def useThreads(self):
        return False

    def useTimer(self):
        return True

    def fetchAll(self, cursor, tablename, where_filter, fields, curname):
        if curname not in self.rowsFetched.keys():
            self.rowsFetched[curname] = 0
        
        rowsF = []
        try:
            rows = list(self.cursorsArray_[curname])
            if self.rowsFetched[curname] < len(rows):
                i = 0
                for row in rows:
                    i += 1
                    if i > self.rowsFetched[curname]:
                        rowsF.append(row)

                self.rowsFetched[curname] = i
        except Exception:
            self.logger.error("%s:: fetchAll",self.name_, traceback.format_exc())
        
        return rowsF


    def existsTable(self, name):
        if not self.isOpen():
            return False

        t = FLSqlQuery()
        t.setForwardOnly(True)
        ok = t.exec_(
            "select relname from pg_class where relname = '%s'" % name)
        if ok:
            ok = t.next()

        del t
        return ok

    def sqlCreateTable(self, tmd):
        # util = FLUtil()
        if not tmd:
            return None

        primaryKey = None
        sql = "CREATE TABLE %s (" % tmd.name()
        seq = None

        fieldList = tmd.fieldList()

        unlocks = 0
        for field in fieldList:
            if field.type() == "unlock":
                unlocks += 1

        if unlocks > 1:
            qWarning(u"%s : No se ha podido crear la tabla %s" % (self.name_, tmd.name()))
            qWarning(u"%s : Hay mas de un campo tipo unlock. Solo puede haber uno." % self.name_)
            return None

        i = 1
        for field in fieldList:
            sql = sql + field.name()
            if field.type() == "int":
                sql += " INT"
            elif field.type() in ["uint","serial"]:
                sql += " INT UNSIGNED"
            elif field.type() in ("bool", "unlock"):
                sql += " BOOL"
            elif field.type() == "double":
                sql += " DECIMAL(%s,%s)" % (field.partInteger() + field.partDecimal() +5 , field.partDecimal() + 5)
            elif field.type() == "time":
                sql += " TIME"
            elif field.type() == "date":
                sql += " DATE"
            elif field.type() in ["pixmap","stringlist"]:
                sql += " MEDIUMTEXT"
            elif field.type() == "string":
                if field.length() > 0:
                    if field.length() > 255:
                        sql += " VARCHAR"
                    else:
                        sql += " CHAR"
                    
                    sql += "(%s)" % field.length()
                else:
                    sql += " CHAR(255)"
                    
            elif field.type() == "bytearray":
                sql = sql + " LONGBLOB"


            if field.isPrimaryKey():
                if primaryKey is None:
                    sql += " PRIMARY KEY"
                    primaryKey = field.name()
                else:
                    qWarning(QApplication.tr("FLManager : Tabla-> ") + tmd.name() +
                             QApplication.tr(" . Se ha intentado poner una segunda clave primaria para el campo ") +
                             field.name() + QApplication.tr(" , pero el campo ") + primaryKey +
                             QApplication.tr(" ya es clave primaria. Sólo puede existir una clave primaria en FLTableMetaData,"
                                             " use FLCompoundKey para crear claves compuestas."))
                    return None
            else:
                if field.isUnique():
                    sql += " UNIQUE"
                if not field.allowNull():
                    sql += " NOT NULL"
                else:
                    sql += " NULL"

            if not i == len(fieldList):
                sql += ","
                i = i + 1

        engine = ") ENGINE=INNODB" if self.alias_ is "FLMYSQL_INNODB" else ") ENGINE=MyISAM"
        sql += engine
        
        sql += " DEFAULT CHARACTER SET = utf8  COLLATE = utf8_bin"
        
        qWarning("NOTICE: CREATE TABLE (%s%s)" % (tmd.name(), engine))

        return sql

    def mismatchedTable(self, table1, tmd_or_table2, db_):
        if isinstance(tmd_or_table2, str):
            mtd = db_.manager().metadata(tmd_or_table2, True)
            if not mtd:
                return False

            return False

        else:
            return self.mismatchedTable(table1, tmd_or_table2.name(), db_)
        
    def normalizeValue(self, text):
        if text and text.find("\\n") > -1:
            text = text.replace("\\n", "\\\\n")
        if text and text.find('\\"') > -1:
            text = text.replace('\\"', '\\\\"')
        return None if text is None else text.replace("'", "''")

    def cascadeSupport(self):
        return True

    def canDetectLocks(self):
        return True

    def desktopFile(self):
        return False

    def execute_query(self, q):

        if not self.isOpen():
            qWarning("MySQLDriver::execute_query. DB is closed")
            return False
        cursor = self.cursor()
        try:
            cursor.execute(q)
        except Exception:
            
            self.setLastError(
                "No se puedo ejecutar la siguiente query %s" % q, q)
            qWarning("MySQLDriver:: No se puedo ejecutar la siguiente query %s\n %s" % (q, traceback.format_exc()))
