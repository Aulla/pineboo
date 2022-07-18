"""
Tests for known bugs on qsa.
"""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.application import types
from pineboolib.application.parsers.parser_qsa.postparse import pythonify_string as qs2py
from pineboolib.qsa import qsa


class TestKnownBugs(unittest.TestCase):
    """Test known bugs."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_isloadedmodule(self) -> None:
        """Test bug where sys.isLoadedModule seems to be None."""

        fn_test = types.function("module", "return sys.isLoadedModule(module);")
        self.assertEqual(fn_test("random_module"), False)
        self.assertEqual(fn_test("sys"), True)

    def test_mid(self) -> None:
        """Test str.mid(5, 2)."""

        value_1 = 'var cadena:String = "abcdefg";\ncadena.mid(5, 2);'
        self.assertEqual(qs2py(value_1), 'cadena: str = "abcdefg"\ncadena[5 : 5 + 2]\n')

        value_2 = 'var cadena:String = "abcdefg";\ncadena.mid(5);'
        self.assertEqual(qs2py(value_2), 'cadena: str = "abcdefg"\ncadena[0 + 5 :]\n')

    def test_system_get_env(self) -> None:
        """Check that qsa.System.getenv () works correctly."""

        qsa.System.setenv("TEST_PINEBOO", "¡hola!")

        self.assertEqual(qsa.System.getenv("TEST_PINEBOO"), "¡hola!")

    def test_self(self) -> None:
        """Test self."""

        value = "aqApp.self()"
        self.assertEqual(qs2py(value), "qsa.aqApp.self_()\n")

    def test_index_of(self) -> None:
        """Check indexOf translation."""

        value = """var text_:String = "test@test.test";\nif (text_.indexOf("@") == -1){\ndebug("ok");}"""
        self.assertEqual(
            qs2py(value),
            """text_: str = "test@test.test"\nif text_.index("@") == -1:\n    qsa.debug("ok")\n""",
        )

    def test_reg_exp(self) -> None:
        """Test regExp parser."""
        value = """var reg_exp:RegExp = new RegExp( "''" );\nreg_exp.global = true;"""
        self.assertEqual(
            qs2py(value), """reg_exp: "qsa.RegExp" = qsa.RegExp("''")\nreg_exp.global_ = True\n"""
        )

        value2 = """var reg_exp:RegExp = new RegExp( " " );\nreg_exp.global = true;\nvar texto:String = "UNO DOS".replace(reg_exp, "_");"""
        self.assertEqual(
            qs2py(value2),
            """reg_exp: \"qsa.RegExp\" = qsa.RegExp(" ")\nreg_exp.global_ = True\ntexto: str = qsa.replace("UNO DOS", reg_exp, "_")\n""",
        )

        value3 = """var reg_exp:RegExp = new RegExp( " " );\nreg_exp.global = true;\n
        var texto:String = "UNO DOS".replace(reg_exp, "_").lower();"""
        self.assertEqual(
            qs2py(value3),
            """reg_exp: \"qsa.RegExp\" = qsa.RegExp(" ")\nreg_exp.global_ = True\n"""
            + """texto: str = qsa.replace("UNO DOS", reg_exp, "_").lower()\n""",
        )

    def test_from_project(self) -> None:
        """Test from_project parser."""
        value_1 = (
            'qsa.sys.AQTimer.singleShot(0, qsa.from_project("formescarrosproveedor").reject)\n'
        )
        self.assertEqual(qs2py("sys.AQTimer.singleShot(0, formescarrosproveedor.reject);"), value_1)
        value_2 = (
            'qsa.sys.AQTimer.singleShot(0, qsa.from_project("formRecordflmodules").iface.prueba)\n'
        )
        self.assertEqual(
            qs2py("sys.AQTimer.singleShot(0, formRecordflmodules.iface.prueba);"), value_2
        )
        value_3 = 'qsa.sys.AQTimer.singleShot(0, qsa.from_project("flfactppal").iface.test)\n'
        self.assertEqual(qs2py("sys.AQTimer.singleShot(0, flfactppal.iface.test);"), value_3)

        value_4 = '_fP: Any = qsa.from_project("flfactppal").iface\n'
        self.assertEqual(qs2py("var _fP = flfactppal.iface;"), value_4)

    def test_multiples_if(self) -> None:
        """Check stackoverflow when parsing."""

        cadena = """var fN : String ="uno0";
                    if (fN == "uno0") {
                        debug(fN);
                        }
                    else if (fN == "dos0") {
                        debug(fN)
                        }
                    else if (fN == "tres0") {
                        debug(fN);
                        }
                    else if (fN == "cuatro0") {
                        debug(fN);
                        }
                    else if (fN == "cinco0") {
                        debug(fN);
                        }
                    else if (fN == "seis0") {
                        debug(fN);
                        }
                    else if (fN == "siete0") {
                        debug(fN);
                        }
                    else if (fN == "ocho0") {
                            debug(fN);
                            }
                    else if (fN == "nueve0") {
                        debug(fN);
                        }
                    else if (fN == "diez0") {
                        debug(fN);
                        }
                    else if (fN == "uno0") {
                        debug(fN);
                        }
                    else if (fN == "dos0") {
                        debug(fN);
                        }
                    else if (fN == "tres0") {
                        debug(fN);
                        }
                    else if (fN == "cuatro0") {
                        debug(fN);
                        }
                    else if (fN == "cinco0") {
                        debug(fN);
                        }
                    else if (fN == "seis0") {
                        debug(fN);
                        }
                    else if (fN == "siete0") {
                        debug(fN);
                        }
                    else if (fN == "ocho0") {
                            debug(fN);
                            }
                    else if (fN == "nueve0") {
                        debug(fN);
                        }
                    else if (fN == "diez0") {
                        debug(fN);
                        }
                    else if (fN == "dos0") {
                        debug(fN);
                        }
                    else if (fN == "tres0") {
                        debug(fN);
                        }
                    else if (fN == "cuatro0") {
                        debug(fN);
                        }
                    else if (fN == "cinco0") {
                        debug(fN);
                        }
                    else if (fN == "seis0") {
                        debug(fN);
                        }
                    else if (fN == "siete0") {
                        debug(fN);
                        }
                    else if (fN == "ocho0") {
                            debug(fN);
                            }
                    else if (fN == "nueve0") {
                        debug(fN);
                        }
                    else if (fN == "diez0") {
                        debug(fN);
                        }
                    else if (fN == "uno0") {
                        debug(fN);
                        }
                    else if (fN == "dos0") {
                        debug(fN);
                        }
                    else if (fN == "tres0") {
                        debug(fN);
                        }
                    else if (fN == "cuatro0") {
                        debug(fN);
                        }
                    else if (fN == "cinco0") {
                        debug(fN);
                        }
                    else if (fN == "seis0") {
                        debug(fN);
                        }
                    else if (fN == "siete0") {
                        debug(fN);
                        }
                    else if (fN == "ocho0" || fN == "once0") {
                            debug(fN);
                            }
                    else if (fN == "nueve0") {
                        debug(fN);
                        }
                    else if (fN == "diez0") {
                        debug(fN);
                        }

                    return fN;"""

        cadena_result = qs2py(cadena)
        self.assertFalse(cadena_result.find("not-known-seq") > -1)

    def test_from_project_2(self) -> None:
        """Test from_project('sys')."""

        self.assertTrue(hasattr(qsa.from_project("sys"), "iface"))

    def test_flsqlquery_date_null(self) -> None:
        """Test FLSqlQuery date null."""

        cursor = qsa.FLSqlCursor("fltest")
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        self.assertTrue(cursor.commitBuffer())

        qry = qsa.FLSqlQuery()
        qry.setTablesList("fltest")
        qry.setSelect("date_field")
        qry.setFrom("fltest")
        qry.setWhere("1=1 LIMIT 1")
        self.assertTrue(qry.exec_())
        self.assertTrue(qry.first())
        self.assertEqual(str(qry.value(0)), "")

    def test_args(self) -> None:
        """Test translate with args parse."""

        cadena = qs2py(
            """var qryRecargo: FLSqlQuery = new FLSqlQuery;
        var res = util.translate("scripts", "Uno %1 para %2. ¿Desea continuar?")
        .arg(qryRecargo.value("f.codigo"))
        .arg(qryRecargo.value("f.nombrecliente"))"""
        )

        cadena_result = """qryRecargo: \"qsa.FLSqlQuery\" = qsa.FLSqlQuery()
res: Any = qsa.util.translate("scripts", "Uno %s para %s. ¿Desea continuar?") % (
    str(qryRecargo.value("f.codigo")),
    str(qryRecargo.value("f.nombrecliente")),\n)\n"""

        self.assertEqual(cadena, cadena_result)

    def test_args_str_int(self) -> None:
        """Test argStr and argInt."""

        one = """var res= util.translate("scripts", "Hola %1").argStr("Uno");"""
        result_one = """res: Any = qsa.util.translate("scripts", "Hola %s") % (str("Uno"))\n"""

        self.assertEqual(qs2py(one), result_one)

        two = """var res= util.translate("scripts", "Hola %1").argInt("Dos");"""
        result_two = """res: Any = qsa.util.translate("scripts", "Hola %s") % (str("Dos"))\n"""

        self.assertEqual(qs2py(two), result_two)

    def test_array_functions(self) -> None:
        """Test functions array conversion."""

        one = """var cacheFunsEdi = [];
        cacheFunsEdi["uno"]("dos");"""

        result_one = """cacheFunsEdi: Any = qsa.Array()\ncacheFunsEdi["uno"]("dos")\n"""
        self.assertEqual(qs2py(one), result_one)

    def test_number_min_value_and_max_value(self) -> None:
        """Test number min and max value."""
        qsa_one = "var min : Number = Number.MIN_VALUE;"
        result_one = "min = qsa.Number.MIN_VALUE\n"
        self.assertEqual(qs2py(qsa_one), result_one)

        qsa_two = "var max : Number = Number.MAX_VALUE;"
        result_two = "max = qsa.Number.MAX_VALUE\n"
        self.assertEqual(qs2py(qsa_two), result_two)

        self.assertTrue(qsa.Number.MIN_VALUE < 0)
        self.assertTrue(qsa.Number.MAX_VALUE > 0)

    def test_attribute_dict(self) -> None:
        """Test attribute dict converison."""

        att1 = qsa.AttributeDict(
            {"key_prueba1": ("valor_prueba1"), "key_prueba2": ("valor_prueba2")}
        )
        self.assertEqual(att1, {"key_prueba1": "valor_prueba1", "key_prueba2": "valor_prueba2"})

    def test_array_concat(self) -> None:
        """Test array concat simple."""
        array = qsa.Array().concat({"uno": "uno"}, {"dos": "dos"})
        self.assertEqual(array, {"uno": "uno", "dos": "dos"})
        array2 = qsa.Array().concat(["1", "2", "3"], ["5", "6"])
        self.assertEqual(array2, ["1", "2", "3", "5", "6"])

    def test_array_concat2(self) -> None:
        """Test array concat extended."""
        self.maxDiff = None
        codigo = """function getRules()
                    {
                        return new Array().concat(
                            this.getCrudRules('pedidoscli', 'Pedidos de cliente'),
                            [
                                {
                                    "idregla": 'pedidoscli/accion1',
                                    "grupo": 'pedidoscli',
                                    "descripcion": 'Puede ejecutar la accion 1 de pedidos de cliente. Puede ejecutar la accion 1.'
                                },
                                {
                                    "idregla": 'pedidoscli/accion2',
                                    "grupo": 'pedidoscli',
                                    "descripcion": 'Puede ejecutar la accion 2 de pedidos de cliente'
                                }
                            ]
                        );
                    }
                    function getCrudRules(grupo, descripcion)
                    {
                        var crudRules = [
                            {
                                'id': 'get',
                                'desc': 'Puede recibir'
                            },
                            {
                                'id': 'post',
                                'desc': 'Puede crear'
                            },
                            {
                                'id': 'patch',
                                'desc': 'Puede modificar'
                            },
                            {
                                'id': 'delete',
                                'desc': 'Puede eliminar'
                            }
                        ]
                        var rules = [{
                            'idregla': grupo,
                            'grupo': grupo,
                            'descripcion': descripcion
                        }]
                        for (var i = 0; i < crudRules.length; i++) {
                            rules.push({
                                'idregla': grupo + '/' + crudRules[i].id,
                                'grupo': grupo,
                                'descripcion': crudRules[i].desc + ' ' + descripcion.toLowerCase()
                            })
                        }
                        return rules;
                    }
                    """

        cadena_result = qs2py(codigo)
        ok_result = """def getRules(self):
    return qsa.Array().concat(
        self.getCrudRules("pedidoscli", "Pedidos de cliente"),
        qsa.Array(
            [
                qsa.AttributeDict(
                    {
                        "idregla": ("pedidoscli/accion1"),
                        "grupo": ("pedidoscli"),
                        "descripcion": (
                            "Puede ejecutar la accion 1 de pedidos de cliente. Puede ejecutar la accion 1."
                        ),
                    }
                ),
                qsa.AttributeDict(
                    {
                        "idregla": ("pedidoscli/accion2"),
                        "grupo": ("pedidoscli"),
                        "descripcion": ("Puede ejecutar la accion 2 de pedidos de cliente"),
                    }
                ),
            ]
        ),
    )


def getCrudRules(self, grupo, descripcion):
    crudRules: Any = qsa.Array(
        [
            qsa.AttributeDict(
                {
                    "id": ("get"),
                    "desc": ("Puede recibir"),
                }
            ),
            qsa.AttributeDict(
                {
                    "id": ("post"),
                    "desc": ("Puede crear"),
                }
            ),
            qsa.AttributeDict(
                {
                    "id": ("patch"),
                    "desc": ("Puede modificar"),
                }
            ),
            qsa.AttributeDict(
                {
                    "id": ("delete"),
                    "desc": ("Puede eliminar"),
                }
            ),
        ]
    )
    rules: Any = qsa.Array(
        [
            qsa.AttributeDict(
                {
                    "idregla": (grupo),
                    "grupo": (grupo),
                    "descripcion": (descripcion),
                }
            )
        ]
    )
    i: Any = 0
    while_pass = True
    while i < qsa.length(crudRules):
        if not while_pass:
            i += 1
            while_pass = True
            continue
        while_pass = False
        rules.append(
            qsa.AttributeDict(
                {
                    "idregla": (qsa.ustr(grupo, "/", crudRules[i].id)),
                    "grupo": (grupo),
                    "descripcion": (qsa.ustr(crudRules[i].desc, " ", descripcion.lower())),
                }
            )
        )
        i += 1
        while_pass = True
        try:
            i < qsa.length(crudRules)
        except Exception:
            break

    return rules
"""
        self.assertEqual(cadena_result, ok_result)

    def test_execMainScript(self) -> None:
        """Test aqApp.execMainScript."""

        from pineboolib.qsa import qsa

        fun_ = qsa.from_project("sys").iface.execMainScript
        self.assertTrue(fun_ is not None)

    def test_session(self) -> None:
        """Test session conversion."""

        qsa = 'if (sys.interactiveGUI() == "Django") { \nvar sessi = new session();}'
        result = 'if qsa.sys.interactiveGUI() == "Django":\n    sessi: Any = qsa.session()\n'
        self.assertEqual(qs2py(qsa), result)

        qsa2 = 'if (sys.interactiveGUI() == "Django") { \nvar session = new session();}'
        result2 = 'if qsa.sys.interactiveGUI() == "Django":\n    session: Any = qsa.session()\n'
        self.assertEqual(qs2py(qsa2), result2)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
