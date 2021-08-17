"""
Tests for Orm on qsa.
"""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa


class TestOrm(unittest.TestCase):
    """Test Orm."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_load(self) -> None:
        """Load model."""
        qsa.thread_session_new()
        class1_ = qsa.from_project("flareas_orm")
        obj_ = qsa.orm_("flareas")()
        self.assertEqual(class1_, obj_.__class__)
        qsa.thread_session_free()

    # ===============================================================================
    #     def test_sessions_isolation(self) -> None:
    #
    #         session1_ = qsa.session()
    #         session2_ = qsa.session("dbAux")
    #         session3_ = qsa.session("aux")
    #
    #         self.assertNotEqual(session1_, session2_)
    #         self.assertNotEqual(session1_, session3_)
    #         self.assertNotEqual(session2_, session3_)
    # ===============================================================================

    def test_create_object(self) -> None:
        """Create object."""

        class_ = qsa.from_project("flareas_orm")
        self.assertTrue(class_)

        obj_ = class_()

        setattr(obj_, "bloqueo", True)
        setattr(obj_, "idarea", "A")
        setattr(obj_, "descripcion", "Area A")

        self.assertEqual(obj_.idarea, "A")
        self.assertEqual(obj_.bloqueo, True)
        self.assertEqual(getattr(obj_, "descripcion", ""), "Area A")

    def test_insert_to_database(self) -> None:
        """Insert object to database."""

        session_ = qsa.session()
        class_ = qsa.from_project("flareas_orm")

        obj_ = class_()

        setattr(obj_, "bloqueo", True)
        setattr(obj_, "idarea", "A")
        setattr(obj_, "descripcion", "Area A")
        session_.begin()
        session_.add(
            obj_
        )  # Introduce el nuevo registro en la BD. A partir de ahora los cambios posteriores se guardarán en la BD.
        # res_1 = session_.execute("SELECT idarea FROM flareas WHERE idarea = 'A'")
        # self.assertFalse(res_1.returns_rows)
        session_.flush()  # Aplica el cambio en la BD.
        res_2 = session_.execute("SELECT idarea FROM flareas WHERE idarea = 'A'")
        self.assertTrue(res_2.returns_rows)

        obj2_ = session_.query(class_).get("A")  # Recupera el registro de la BD

        self.assertEqual(obj_, obj2_)
        session_.rollback()

    def test_delete_from_database(self) -> None:
        """Insert object to database."""

        session_ = qsa.session()
        class_ = qsa.from_project("flareas_orm")

        obj_ = class_()

        setattr(obj_, "bloqueo", True)
        setattr(obj_, "idarea", "A")
        setattr(obj_, "descripcion", "Area A")

        session_.begin()
        session_.add(obj_)
        session_.commit()  # Se cierra la sesión (Transacción)

        session_2 = qsa.session()
        obj2_ = session_2.query(class_).get("A")  # Recupera el registro de la BD
        self.assertTrue(obj2_)
        session_2.begin()
        session_2.delete(obj2_)
        session_2.commit()

        session_3 = qsa.session()
        obj3_ = session_3.query(class_).get("A")  # Recupera el registro de la BD
        self.assertFalse(obj3_)

    def test_modify_data(self) -> None:
        """Insert object to database."""

        session_ = qsa.thread_session_new()
        class_ = qsa.from_project("flareas_orm")

        obj_ = class_()

        setattr(obj_, "bloqueo", True)
        setattr(obj_, "idarea", "B")
        setattr(obj_, "descripcion", "Area B")
        session_.begin()
        self.assertTrue(obj_.save())
        # session_.add(obj_)  # Introduce el nuevo registro en la BD
        session_.commit()
        session_2 = qsa.session()
        session_2.begin()
        obj2_ = session_2.query(class_).get("B")  # Recupera el registro de la BD
        self.assertEqual(obj2_.descripcion, "Area B")
        obj2_.descripcion = "Area B modificada"
        session_2.commit()  # Guarda el cambio permanentemente.

        session_3 = qsa.session()
        obj3_ = session_3.query(class_).get("B")
        self.assertEqual(obj3_.descripcion, "Area B modificada")
        qsa.thread_session_free()

    def test_legacy_metadata(self) -> None:
        """Compares metadata with rom metadata."""

        aq_app = qsa.aqApp

        class_ = qsa.from_project("flareas_orm")

        metadata = aq_app.db().manager().metadata("flareas")
        self.assertTrue(metadata)
        if metadata is not None:
            self.assertEqual(metadata.name(), class_.legacy_metadata["name"])
            self.assertEqual(metadata.alias(), class_.legacy_metadata["alias"])

            result = None
            for field in class_.legacy_metadata["fields"]:
                if field["name"] == "bloqueo":
                    result = field["default"]
                    break

            self.assertEqual(
                metadata.field("bloqueo").defaultValue(), result  # type: ignore [union-attr]
            )

    def test_save_points(self) -> None:
        """Save points."""

        session_ = (
            qsa.thread_session_new()
        )  # implica nueva Transaccion si en la llama anterior se hizo rollback o commit.
        # Si no continua en la transaccion que se abrio la última vez

        class_ = qsa.from_project("flareas_orm")
        obj_ = class_()
        obj_.idarea = "C"
        obj_.descripcion = "Descripción C"
        obj_.bloqueo = True
        session_.begin()
        session_.add(obj_)

        session_.begin_nested()  # Save point

        obj_.descripcion = "Descripción Nueva"

        obj2_ = session_.query(class_).get("C")

        self.assertEqual(obj_.descripcion, "Descripción Nueva")
        self.assertEqual(obj2_.descripcion, "Descripción Nueva")

        session_.rollback()  # rollback save_point

        self.assertEqual(obj_.descripcion, "Descripción C")

        session_.rollback()  # rollback transaccion
        qsa.thread_session_free()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
