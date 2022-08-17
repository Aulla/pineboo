# -*- coding: utf-8 -*-
"""
Module dgi_qt3ui.

Loads old Qt3 UI files and creates a Qt5 UI.
"""
from importlib import import_module

from PyQt6 import QtCore, QtGui, QtWidgets  # type: ignore[import]
from xml.etree import ElementTree as ET
from binascii import unhexlify
from pineboolib import logging
import zlib

from pineboolib.core.utils.utils_base import load2xml
from pineboolib import application
from pineboolib.application import connections


from pineboolib.q3widgets import qmainwindow, qlistview, qtoolbar, qmenu, qaction, qspinbox

from pineboolib.core import settings


from typing import Optional, Tuple, Callable, List, Dict, Any, cast, Type, Union

ICONS: Dict[str, Any] = {}
ROOT = None
LOGGER = logging.get_logger(__name__)


class Options:
    """
    Store module options.

    ***DEPRECATED***
    """

    DEBUG_LEVEL = 100


# TODO: Refactorizar este fichero como una clase. ICONS es la lista de iconos
#      para un solo formulario. Debe existir una clase LoadUI y que ICONS sea
#      una variable de ésta. Para cada nuevo formulario se debería instanciar
#      una nueva clase.


# FIXME: widget is QWidget type but Qt5-Stubs for findChild reports QObject instead of Optional[QObject]
def load_ui(form_path: str, widget: Any, parent: Optional["QtWidgets.QWidget"] = None) -> None:
    """
    Load Qt3 UI file from eneboo.

    widget: Provide a pre-created widget and this function will store UI contents on it.
    parent: Probably deprecated.
    """
    global ICONS, ROOT
    # parser = etree.XMLParser(
    #    ns_clean=True,
    #    encoding="UTF-8",
    #    remove_blank_text=True,
    # )

    tree = load2xml(form_path)

    if not tree:
        return

    ROOT = tree.getroot()
    ICONS = {}

    if parent is None:
        parent = widget

    # if application.PROJECT.DGI.localDesktop():
    widget.hide()

    for xmlimage in ROOT.findall("images//image"):
        load_icon(xmlimage)

    for xmlwidget in ROOT.findall("widget"):
        LoadWidget(xmlwidget, widget, parent)

    # print("----------------------------------")
    # for xmlwidget in ROOT.xpath("actions"):
    #     LoadWidget(xmlwidget, widget, parent)
    # print("----------------------------------")

    # Debe estar despues de LoadWidget porque queremos el valor del UI de Qt3
    formname = widget.objectName()
    LOGGER.info("form: %s", formname)

    # Cargamos actions...
    # for action in ROOT.findall("actions//action"):
    #    load_action(action, widget)

    # Cargamos menubar ...
    xmlmenubar = ROOT.find("menubar")
    # print("Cargamos menubar!")
    if xmlmenubar:
        load_menu_bar(xmlmenubar, widget)

    # Cargamos toolbars ...
    # print("Cargamos toolbar!")
    for xmltoolbar in ROOT.findall("toolbars//toolbar"):
        load_tool_bar(xmltoolbar, widget)

    for xmlconnection in ROOT.findall("connections//connection"):
        sender_elem = xmlconnection.find("sender")
        signal_elem = xmlconnection.find("signal")
        receiv_elem = xmlconnection.find("receiver")
        slot_elem = xmlconnection.find("slot")

        if sender_elem is None or signal_elem is None or receiv_elem is None or slot_elem is None:
            continue

        sender_name = sender_elem.text
        signal_name = signal_elem.text
        receiv_name = receiv_elem.text
        slot_name = slot_elem.text

        if sender_name is None:
            raise ValueError("no se encuentra sender_name")
        if signal_name is None:
            raise ValueError("no se encuentra signal_name")
        if receiv_name is None:
            raise ValueError("no se encuentra receiv_name")
        if slot_name is None:
            raise ValueError("no se encuentra slot_name")

        receiver: Any = None
        if isinstance(widget, (qmainwindow.QMainWindow, QtWidgets.QMainWindow)):
            if signal_name == "activated()":
                signal_name = "triggered()"

        if sender_name == formname:
            sender = widget
        else:
            senders = widget.findChildren(QtCore.QObject, sender_name)
            for sender in senders:

                # if not application.PROJECT.DGI.localDesktop():
                #    wui = hasattr(widget, "ui_") and sender_name in widget.ui_
                #    if sender is None and wui:
                #        sender = widget.ui_[sender_name]

                sg_name = signal_name

                if signal_name.find("(") > -1:
                    sg_name = signal_name[: signal_name.find("(")]

                sl_name = slot_name
                if slot_name.find("(") > -1:
                    sl_name = slot_name[: slot_name.find("(")]

                if sender is None:
                    LOGGER.debug("Connection sender not found:%s", sender_name)

                if receiv_name == formname:
                    # fn_name = slot_name.rstrip("()")
                    fn_name = slot_name[: slot_name.find("(")]
                    LOGGER.debug(
                        "Conectando de UI a QS: (%r.%r -> %r.%r)",
                        sender_name,
                        signal_name,
                        receiv_name,
                        fn_name,
                    )

                    ifx = None
                    if not widget.inherits("QMainWindow"):
                        parent = widget.parent()
                        if parent:
                            ifx = getattr(parent, "iface", None)
                    else:
                        if sender_name in application.PROJECT.actions.keys():
                            receiver = application.PROJECT.actions[sender_name]._master_widget
                        else:
                            if receiver is None:
                                if (
                                    receiv_name == widget.__class__.__name__
                                    or receiv_name == widget.objectName()
                                ):
                                    receiver = widget

                    ifx = widget
                    # if hasattr(widget, "iface"):
                    #    ifx = widget.iface
                    if hasattr(ifx, fn_name):
                        try:

                            # getattr(sender, sg_name).connect(
                            #    getattr(ifx, fn_name))
                            connections.connect(sender, signal_name, ifx, fn_name)
                        except Exception:
                            LOGGER.debug(
                                "Error connecting: %s %s %s %s %s",
                                sender,
                                signal_name,
                                receiver,
                                slot_name,
                                getattr(ifx, fn_name),
                            )
                        continue

                if receiver is None:
                    receiver = widget.findChild(
                        QtCore.QObject,
                        receiv_name,
                        QtCore.Qt.FindChildOption.FindChildrenRecursively,
                    )

                if receiver is None:
                    from pineboolib.application.safeqsa import SafeQSA

                    receiver = SafeQSA.get_any(receiv_name)

                if receiver is None and receiv_name == "FLWidgetApplication":
                    if sender_name in application.PROJECT.actions.keys():
                        receiver = application.PROJECT.actions[sender_name]
                    else:
                        LOGGER.debug("Sender action %s not found. Connection skiped", sender_name)
                        continue

                if receiver is None:
                    LOGGER.debug("Connection receiver not found:%s", receiv_name)

                if sender is None or receiver is None:
                    continue

                if slot_name in ("openDefaultForm()", "execDefaultScript()"):
                    continue

                elif hasattr(receiver, "iface"):
                    # iface = getattr(receiver, "iface")
                    # try:
                    #    receiver.connect(
                    #        sender,
                    #        signal_name,
                    #        receiver,
                    #        "%s%s" % ("iface." if hasattr(iface, sl_name) else "", slot_name),
                    #    )
                    #     getattr(sender, sg_name).connect(getattr(iface, sl_name))
                    # except Exception:
                    #    LOGGER.exception(
                    #        "Error connecting: %s:%s %s.iface:%s", sender, signal_name, receiver, slot_name
                    #    )
                    LOGGER.warning(
                        "DEPRECATED: This type of connection must be made in the module init: %s %s %s %s",
                        sender_name,
                        signal_name,
                        receiv_name,
                        slot_name,
                    )
                    continue

                elif hasattr(receiver, sl_name):
                    try:
                        getattr(sender, sg_name).connect(getattr(receiver, sl_name))
                    except Exception:
                        LOGGER.exception(
                            "Error connecting: %s:%s %s:%s",
                            sender,
                            signal_name,
                            receiver,
                            slot_name,
                        )
                else:
                    LOGGER.error(
                        "Error connecting: %s:%s %s:%s (no candidate found)",
                        sender,
                        signal_name,
                        receiver,
                        slot_name,
                    )

    widget.show()


def load_tool_bar(xml: ET.Element, widget: QtWidgets.QMainWindow) -> None:
    """
    Load UI Toolbar from XML and store it into widget.

    widget: A pre-created widget to store the toolbar.
    """
    name_elem = xml.find("./property[@name='name']/cstring")
    label_elem = xml.find("./property[@name='label']/string")
    if name_elem is None or label_elem is None:
        raise Exception("Unable to find required name and label properties")

    name = name_elem.text or ""
    label = label_elem.text

    tool_bar = qtoolbar.QToolBar(name)
    tool_bar.setObjectName(name)
    tool_bar.label = label
    for action in xml:
        if action.tag == "action":
            name = action.get("name") or "action"
            new_action = tool_bar.addAction(name)
            new_action.setObjectName(name)
            # print("**", name, new_action, tool_bar)
            load_action(action, widget, new_action)
            # print("**", new_action.objectName())
            # clone_action(new_action, widget)

            # FIXME!!, meter el icono y resto de datos!!
        elif action.tag == "separator":
            separator = tool_bar.addSeparator()
            separator.setObjectName("separator")
        elif action.tag == "widget":
            new_widget = WidgetResolver.get_widget_class(action.get("class") or "")(tool_bar)
            LoadWidget(action, new_widget, None, tool_bar)
            tool_bar.addWidget(new_widget)

    widget.addToolBar(tool_bar)
    widget.addToolBarBreak()


def load_menu_bar(xml: "ET.Element", widget: "QtWidgets.QWidget") -> None:
    """
    Load a menu bar into widget.

    widget: pre-created widget to store the object.
    """

    if isinstance(widget, qmainwindow.QMainWindow):
        menu_bar = widget.menuBar()
    else:
        menu_bar = QtWidgets.QMenuBar(widget)
        widget.layout().setMenuBar(menu_bar)  # quitamos _layout()
    for item in xml:
        if item.tag == "property":
            name = item.get("name")
            if name == "name":
                cstring = item.find("cstring")
                if cstring is not None and cstring.text is not None:
                    menu_bar.setObjectName(cstring.text)
            elif name == "geometry":
                geo_ = item.find("rect")
                if geo_:
                    geo_x = geo_.find("x")
                    geo_y = geo_.find("y")
                    geo_width = geo_.find("width")
                    geo_height = geo_.find("height")

                    pos_x = geo_x.text if geo_x else None
                    pos_y = geo_y.text if geo_y else None
                    width = geo_width.text if geo_width else None
                    height = geo_height.text if geo_height else None
                    if pos_x is None or pos_y is None or width is None or height is None:
                        continue
                    menu_bar.setGeometry(int(pos_x), int(pos_y), int(width), int(height))
            elif name in ("acceptDrops", "defaultUp"):
                bool_elem = item.find("bool")
                if bool_elem is not None:
                    attr_ = getattr(menu_bar, "set%s%s" % (name[0].upper(), name[1:]))
                    attr_(bool_elem.text == "true")
            elif name == "frameShape":
                continue
            # elif name == "defaultUp":
            #    bool_elem = item.find("bool")
            #    if bool_elem is not None:
            #        menu_bar.setDefaultUp(bool_elem.text == "true")
        elif item.tag == "item":
            process_item(item, menu_bar, widget)


def process_item(
    xml: "ET.Element",
    parent: Union["QtWidgets.QMenuBar", "QtWidgets.QMenu"],
    widget: "QtWidgets.QWidget",
) -> None:
    """
    Process random XML item.

    widget: pre-created widget to store the object.
    """
    name = xml.get("name") or ""
    text = xml.get("text") or ""
    # accel = xml.get("accel")

    menu_ = parent.addMenu(text)
    menu_.setObjectName(name)

    for item in xml:
        if item.tag == "action":
            name_ = item.get("name") or ""
            new_action = menu_.addAction(name_)
            new_action.setObjectName(name_)

            load_action(item, widget, new_action)
            # action.setObjectName(name_)
            # clone_action(action, widget)
        elif item.tag == "item":
            process_item(item, menu_, widget)


def clone_action(action: "QtGui.QAction", widget: "QtWidgets.QWidget") -> None:
    """
    Clone action into widget.

    widget: pre-created widget to store the object.
    used only on loadToolBar and process_item
    """
    real_action = cast(QtGui.QAction, widget.findChild(QtGui.QAction, action.objectName()))
    if real_action is not None:
        action.setText(real_action.text())
        action.setIcon(real_action.icon())
        action.setToolTip(real_action.toolTip())
        if real_action.statusTip():
            action.setStatusTip(real_action.statusTip())
        else:
            action.setStatusTip(real_action.whatsThis())
        action.setWhatsThis(real_action.whatsThis())
        action.triggered.connect(real_action.trigger)  # type: ignore [attr-defined] # noqa: F821
        action.toggled.connect(real_action.toggle)  # type: ignore [attr-defined] # noqa: F821


def load_action(
    action: "ET.Element", widget: "QtWidgets.QWidget", action_widget: "QtGui.QAction" = None
) -> None:
    """
    Load Action into widget.

    widget: pre-created widget to store the object.
    """
    global ICONS
    if action_widget is not None:
        new_action = action_widget
    else:
        new_action = QtGui.QAction(widget)

    action_name = action.get("name")
    for root_action in ROOT.findall("actions//action"):  # type: ignore [union-attr] # noqa: F821
        for property in root_action.findall("property"):
            if property.get("name") == "name":
                cstring = property.find("cstring")
                if cstring is not None:
                    if cstring.text == action_name:
                        menu_text: Optional[str] = None
                        for property2 in root_action.findall("property"):
                            name = property2.get("name")
                            cstring = property2.find("cstring")
                            string = property2.find("string")
                            iconset = property2.find("iconset")

                            if name == "name" and cstring is not None:
                                if action_name == cstring.text:
                                    new_action.setObjectName(cstring.text or "unnamed")
                            elif name == "text" and string is not None:
                                new_action.setText(string.text or "")
                            elif name == "iconSet" and iconset is not None:
                                if iconset.text and iconset.text in ICONS.keys():
                                    new_action.setIcon(ICONS[iconset.text])
                            elif name == "toolTip" and string is not None:
                                new_action.setToolTip(string.text or "")
                            elif name == "statusTip" and string is not None:
                                new_action.setStatusTip(string.text or "")
                            elif name == "whatsThis" and string is not None:
                                new_action.setWhatsThis(string.text or "")
                            elif name == "menuText" and string is not None:
                                menu_text = string.text

                        if menu_text:
                            new_action.setText(menu_text)


class WidgetResolver:
    """
    Resolve classnames into widgets with caching.
    """

    KNOWN_WIDGETS: Dict[str, Type["QtWidgets.QWidget"]] = {}

    @classmethod
    def get_widget_class(resolver_cls, classname: str) -> Type["QtWidgets.QWidget"]:
        """Get a widget class from class name."""
        if classname in resolver_cls.KNOWN_WIDGETS:
            return resolver_cls.KNOWN_WIDGETS[classname]

        cls: Optional["QtWidgets.QWidget"] = None
        mod_name_full = "pineboolib.q3widgets.%s" % classname.lower()
        try:
            mod_ = import_module(mod_name_full)
            cls = getattr(mod_, classname, None)
        except ModuleNotFoundError:
            LOGGER.trace("resolveObject: Module not found %s", mod_name_full)
        except Exception:
            LOGGER.exception("resolveObject: Unable to load module %s", mod_name_full)

        if cls is None:
            mod_name_full = "pineboolib.fllegacy.%s" % classname.lower()
            try:
                mod_ = import_module(mod_name_full)
                cls = getattr(mod_, classname, None)
            except ModuleNotFoundError:
                LOGGER.trace("resolveObject: Module not found %s", mod_name_full)
            except Exception:
                LOGGER.exception("resolveObject: Unable to load module %s", mod_name_full)

        if cls is None:
            cls = getattr(QtWidgets, classname, None)

        if cls is None:
            raise AttributeError("Class %r not found" % classname)

        resolver_cls.KNOWN_WIDGETS[classname] = cls  # type: ignore [assignment]
        return cls  # type: ignore [return-value]


# NOTE: This function may create QAction too, which inherits from QObject, not QWidget.
def create_widget(classname: str, parent: Optional["QtWidgets.QWidget"] = None) -> "QtCore.QObject":
    """
    Create a Widget for given class name.
    """
    # FIXME: Avoid dynamic imports. Also, this is slow.
    try:
        cls = WidgetResolver.get_widget_class(classname)
        return cls(parent)
    except AttributeError:
        LOGGER.warning("WARN: Class name not found in QtWidgets:", classname)
        widgt = QtWidgets.QWidget(parent)
        widgt.setStyleSheet("* { background-color: #fa3; } ")
        return widgt


class LoadWidget:
    """Load a widget."""

    translate_properties = {
        "caption": "windowTitle",
        "name": "objectName",
        "icon": "windowIcon",
        "iconSet": "icon",
        "accel": "shortcut",
        "layoutMargin": "contentsMargins",
    }
    widget: "QtCore.QObject"
    parent: "QtWidgets.QWidget"
    orig_widget: "QtWidgets.QWidget"

    def __init__(
        self,
        xml: "ET.Element",
        widget: "QtCore.QObject",
        parent: Optional["QtCore.QObject"] = None,
        orig_widget: Optional["QtCore.QObject"] = None,
    ) -> None:
        """
        Load a random widget from given XML.
        """
        LOGGER.trace(
            "LoadWidget: xml: %s widget: %s parent: %s orig_widget: %s",
            xml,
            widget,
            parent,
            orig_widget,
        )
        if widget is None:
            raise ValueError
        if parent is None:
            parent = widget
        if orig_widget is None:
            orig_widget = widget
        self.widget = widget
        self.orig_widget = cast(QtWidgets.QWidget, orig_widget)
        self.parent = cast(QtWidgets.QWidget, parent)
        del widget
        del orig_widget
        del parent
        # if application.PROJECT.DGI.localDesktop():
        #    if not hasattr(orig_widget, "ui_"):
        #        orig_widget.ui_ = {}
        # else:
        #    orig_widget.ui_ = {}

        nwidget = None
        if self.widget == self.orig_widget:
            class_ = xml.get("class")
            if class_ is None:
                class_ = type(self.widget).__name__

            nwidget = cast(QtWidgets.QWidget, create_widget(class_, parent=self.orig_widget))
            self.parent = nwidget
        layouts_pending_process: List[Tuple[ET.Element, str]] = []
        properties = []
        unbold_fonts = []
        has_layout_defined = False

        for item in xml:
            if item.tag == "layout":
                # LOGGER.warning("Trying to replace layout. Ignoring. %s, %s", repr(c.tag), widget._layout)
                classname = item.get("class")
                if classname is None:
                    raise Exception("Expected class attr")
                lay_ = getattr(QtWidgets, classname)()
                lay_.setObjectName(item.get("name"))
                self.widget.setLayout(lay_)  # type: ignore [attr-defined] # noqa F821
                continue

            elif item.tag == "property":
                properties.append(item)
                continue

            elif item.tag in ("vbox", "hbox", "grid"):
                if (
                    has_layout_defined
                ):  # nos saltamos una nueva definición del layout ( mezclas de ui incorrectas)
                    # El primer layout que se define es el que se respeta
                    continue

                if item.tag.find("box") > -1:
                    layout_type = "Q%s%sLayout" % (item.tag[0:2].upper(), item.tag[2:])
                else:
                    layout_type = "QGridLayout"

                layout_class = WidgetResolver.get_widget_class(layout_type)
                self.widget._layout = cast(  # type: ignore [attr-defined] # noqa F821
                    QtWidgets.QLayout, layout_class()
                )

                lay_name = None
                lay_margin_v = 2
                lay_margin_h = 2
                lay_spacing = 2
                for property in item.findall("property"):
                    p_name = property.get("name")
                    number_elem = property.find("number")

                    if p_name == "name":
                        lay_name_e = property.find("cstring")
                        if lay_name_e is not None:
                            lay_name = lay_name_e.text
                    elif p_name == "margin":
                        if number_elem is not None:
                            if number_elem.text is None:
                                raise ValueError("margin no contiene valor")
                            lay_margin = int(number_elem.text)

                        if item.tag == "hbox":
                            lay_margin_h = lay_margin
                        elif item.tag == "vbox":
                            lay_margin_v = lay_margin
                        else:
                            lay_margin_h = lay_margin_v = lay_margin

                    elif p_name == "spacing":
                        if number_elem is not None:
                            if number_elem.text is None:
                                raise ValueError("spacing no contiene valor")
                            lay_spacing = int(number_elem.text)
                    elif p_name == "sizePolicy":
                        self.widget.setSizePolicy(  # type: ignore [attr-defined] # noqa F821
                            load_variant(property, self.widget)
                        )

                self.widget._layout.setSizeConstraint(  # type: ignore [attr-defined] # noqa F821
                    QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize
                )
                self.widget._layout.setObjectName(  # type: ignore [attr-defined] # noqa F821
                    lay_name or "layout"
                )
                self.widget._layout.setContentsMargins(  # type: ignore [attr-defined] # noqa F821
                    lay_margin_h, lay_margin_v, lay_margin_h, lay_margin_v
                )
                self.widget._layout.setSpacing(  # type: ignore [attr-defined] # noqa F821
                    lay_spacing
                )

                lay_type = "grid" if item.tag == "grid" else "box"
                layouts_pending_process += [(item, lay_type)]
                has_layout_defined = True
                continue

            elif item.tag == "item":
                if isinstance(self.widget, qmenu.QMenu):
                    continue
                else:
                    prop1: Dict[str, Any] = {}
                    for property_2 in item.findall("property"):
                        key, value = load_property(property_2)
                        prop1[key] = value

                    self.widget.addItem(prop1["text"])  # type: ignore [attr-defined] # noqa F821
                continue

            elif item.tag == "attribute":
                key = item.get("name")
                value = load_variant(item)
                attrs = getattr(self.widget, "_attrs", None)
                if attrs is not None:
                    attrs[key] = value
                else:
                    LOGGER.warning(
                        "qt3ui: [NOT ASSIGNED] attribute %r => %r" % (key, value),
                        self.widget.__class__,
                        repr(item.tag),
                    )
                continue
            elif item.tag == "widget":
                # Si dentro del widget hay otro significa
                # que estamos dentro de un contenedor.
                # Según el tipo de contenedor, los widgets
                # se agregan de una forma u otra.
                classname = item.get("class")
                if classname is None:
                    raise Exception("Expected class attr")
                new_widget = create_widget(classname, parent=self.parent)
                new_widget.hide()  # type: ignore [attr-defined] # noqa F821
                new_widget._attrs = {}  # type: ignore [attr-defined] # noqa F821
                LoadWidget(item, new_widget, self.parent, self.orig_widget)
                prop_name = item.find("./property[@name='name']/cstring")
                new_widget.setContentsMargins(0, 0, 0, 0)  # type: ignore [attr-defined] # noqa F821
                new_widget.show()  # type: ignore [attr-defined] # noqa F821

                if isinstance(self.widget, QtWidgets.QTabWidget):
                    title = new_widget._attrs.get(  # type: ignore [attr-defined] # noqa F821
                        "title", "UnnamedTab"
                    )
                    self.widget.addTab(cast(QtWidgets.QWidget, new_widget), title)
                elif isinstance(self.widget, (QtWidgets.QGroupBox, QtWidgets.QWidget)):
                    lay = getattr(self.widget, "layout")()
                    if not lay and not isinstance(self.widget, qtoolbar.QToolBar):
                        lay = QtWidgets.QVBoxLayout()
                        cast(QtWidgets.QWidget, self.widget).setLayout(lay)

                    if isinstance(self.widget, qtoolbar.QToolBar):
                        if isinstance(new_widget, QtGui.QAction):
                            self.widget.addAction(new_widget)
                        else:
                            self.widget.addWidget(cast(QtWidgets.QWidget, new_widget))
                    else:
                        lay.addWidget(new_widget)
                else:
                    if Options.DEBUG_LEVEL > 50:
                        LOGGER.warning(
                            "qt3ui: Unknown container widget xml tag",
                            self.widget.__class__,
                            repr(item.tag),
                        )
                unbold_fonts.append(cast(QtWidgets.QWidget, new_widget))
                continue

            elif item.tag == "action":
                action_name = item.get("name")
                if ROOT is None:
                    raise Exception("No se encuentra root")

                for xmlaction in ROOT.findall("actions//action"):
                    prop_name = xmlaction.find("./property[@name='name']/cstring")
                    if prop_name is not None and prop_name.text == action_name:
                        self.process_action(xmlaction, cast(QtWidgets.QToolBar, self.widget))
                        continue

                continue

            elif item.tag == "separator":
                cast(QtWidgets.QMenu, self.widget).addSeparator()
                continue

            elif item.tag == "column":
                for property in item.findall("property"):
                    key, value = load_property(property)
                    if key == "text":
                        cast(qlistview.QListView, self.widget).setHeaderLabel(value)
                    elif key == "clickable":
                        cast(qlistview.QListView, self.widget).setClickable(bool(value))
                    elif key == "resizable":
                        cast(qlistview.QListView, self.widget).setResizable(bool(value))

                continue

            LOGGER.info(
                "%s: Unknown widget xml tag %s %s", __name__, self.widget.__class__, repr(item.tag)
            )

        for prop in properties:
            self.process_property(prop)
        for lay, mode_ in layouts_pending_process:
            self.process_layout_box(lay, mode=mode_)
        for new_widget in unbold_fonts:
            font = new_widget.font()
            font.setBold(False)
            font.setItalic(False)
            new_widget.setFont(font)

        # if not application.PROJECT.DGI.localDesktop():
        #    if nwidget is not None and orig_widget.objectName() not in orig_widget.ui_:
        #        orig_widget.ui_[orig_widget.objectName()] = nwidget

    def process_property(self, xmlprop: ET.Element, widget_: Optional[QtCore.QObject] = None):
        """
        Process a XML property from the UI.
        """
        widget: Any
        if widget_ is None:
            widget = self.widget
        else:
            widget = widget_

        set_fn: Optional[Callable] = None
        pname = xmlprop.get("name") or ""
        pname = self.translate_properties.get(pname, pname)
        setpname = "set" + pname[0].upper() + pname[1:]
        if pname == "layoutSpacing":
            set_fn = widget._layout.setSpacing
        elif pname == "margin":
            set_fn = widget.setContentsMargins
        elif pname in ("paletteBackgroundColor", "paletteForegroundColor"):
            set_fn = widget.setStyleSheet
        elif pname == "menuText":
            if isinstance(widget, qaction.QAction):
                return
            else:
                set_fn = widget.menuText
        elif pname == "movingEnabled":
            set_fn = widget.setMovable
        elif pname == "toggleAction":
            set_fn = widget.setChecked
        elif pname == "label" and isinstance(widget, qtoolbar.QToolBar):
            return
        elif pname == "maxValue" and isinstance(widget, qspinbox.QSpinBox):
            set_fn = widget.setMaximum
        elif pname == "minValue" and isinstance(widget, qspinbox.QSpinBox):
            set_fn = widget.setMinimum
        elif pname == "lineStep" and isinstance(widget, qspinbox.QSpinBox):
            set_fn = widget.setSingleStep
        elif pname == "newLine":
            set_fn = cast(QtWidgets.QMainWindow, self.orig_widget).addToolBarBreak
        elif pname == "functionGetColor":
            set_fn = widget.setFunctionGetColor
        elif pname == "cursor":
            # Ignore "cursor" styles, this is for blinking cursor styles
            # not needed.
            return
        elif pname == "iconText":
            set_fn = widget.setWindowIconText

        else:
            set_fn = getattr(widget, setpname, None)

        if set_fn is None:
            LOGGER.warning("qt3ui: Missing property %s for %r", pname, widget.__class__)
            return

        value: Any

        if pname == "contentsMargins" or pname == "layoutSpacing":
            try:
                value = int(xmlprop.get("stdset", "0"))
                value //= 2
            except Exception:
                value = 0
            if pname == "contentsMargins":
                value = QtCore.QMargins(value, value, value, value)

        elif pname == "margin":
            try:
                value = load_variant(xmlprop)
            except Exception:
                value = 0
            value = QtCore.QMargins(value, value, value, value)

        elif pname == "paletteBackgroundColor":
            fg_color = widget.palette().color(QtGui.QPalette.ColorRole.Window).name()
            bg_color = load_variant(xmlprop).name()
            value = "color: %s; background-color: %s" % (fg_color, bg_color)

        elif pname == "paletteForegroundColor":
            bg_color = widget.palette().color(QtGui.QPalette.ColorRole.WindowText).name()
            fg_color = load_variant(xmlprop).name()

            if bg_color != fg_color:  # Evitamos todo negro
                value = "color: %s; background-color: %s" % (fg_color, bg_color)
            else:
                value = "color: %s" % fg_color

        elif pname in ["windowIcon", "icon"]:
            value1 = load_variant(xmlprop, widget)
            # FIXME: Not sure if it should return anyway
            if isinstance(value1, str):
                LOGGER.warning("Icono %s.%s no encontrado.", widget.objectName(), value1)
                return
            else:
                if value1 is None:
                    return
                value = value1
        elif pname == "buddy":
            control_name = load_variant(xmlprop, widget)
            value = None
            for child in self.orig_widget.children():
                if child.objectName() == control_name:
                    value = child
                    break
            if value is None:
                LOGGER.warning("No se encuentra %s en %s", control_name, self.orig_widget)
        else:
            value = load_variant(xmlprop, widget)
        try:
            set_fn(value)
        except Exception:
            LOGGER.exception(
                "Error processing property %s with value %s. Original XML: %s",
                pname,
                value,
                ET.tostring(xmlprop).replace(b" ", b"").replace(b"\n", b""),
            )
            # if Options.DEBUG_LEVEL > 50:
            #    print(e, repr(value))
            # if Options.DEBUG_LEVEL > 50:
            #    print(etree.ET.tostring(xmlprop))

    def process_action(self, xmlaction: ET.Element, tool_bar: QtWidgets.QToolBar):
        """
        Process a QAction.
        """
        action = cast(QtGui.QAction, create_widget("QAction"))
        for item in xmlaction:
            action_name = item.get("name")
            if action_name in self.translate_properties:
                action_name = self.translate_properties[action_name]

            self.process_property(item, action)
        tool_bar.addAction(action)
        # orig_widget.ui_[action.objectName()] = action

    def process_layout_box(self, xmllayout, widget=None, mode="box"):
        """Process layouts from UI."""
        if widget is None:
            widget = self.widget
        for item in xmllayout:
            try:
                row = int(item.get("row")) or 0
                col = int(item.get("column")) or 0
            except Exception:
                row = col = 0

            if item.tag == "property":  # Ya se han procesado previamente ...
                continue
            elif item.tag == "widget":
                new_widget = create_widget(item.get("class"), parent=widget)
                # FIXME: Should check interfaces.
                from pineboolib.q3widgets import qbuttongroup, qtoolbutton

                if isinstance(widget, qbuttongroup.QButtonGroup):
                    if isinstance(new_widget, qtoolbutton.QToolButton):
                        widget.addButton(new_widget)
                        continue

                LoadWidget(item, new_widget, self.parent, self.orig_widget)
                # path = c.find("./property[@name='name']/cstring").text
                # if not application.PROJECT.DGI.localDesktop():
                #    orig_widget.ui_[path] = new_widget
                # if application.PROJECT.DGI.localDesktop():
                #    new_widget.show()
                if mode == "box":
                    try:
                        widget._layout.addWidget(new_widget)
                    except Exception:
                        LOGGER.warning(
                            "qt3ui: No se ha podido añadir %s a %s", new_widget, widget._layout
                        )

                elif mode == "grid":
                    row_span = item.get("rowspan") or 1
                    col_span = item.get("colspan") or 1
                    try:
                        widget._layout.addWidget(new_widget, row, col, int(row_span), int(col_span))
                    except Exception:
                        LOGGER.warning("qt3ui: No se ha podido añadir %s a %s", new_widget, widget)
                        LOGGER.trace("Detalle:", stack_info=True)

            elif item.tag == "spacer":
                # sH = None
                # sV = None
                hor_policy = QtWidgets.QSizePolicy.Policy.Fixed
                ver_policy = QtWidgets.QSizePolicy.Policy.Fixed
                orient_ = None
                policy_ = QtWidgets.QSizePolicy.Policy.Expanding
                row_span = item.get("rowspan") or 1
                col_span = item.get("colspan") or 1
                # policy_name = None
                spacer_name = None
                for property in item.findall("property"):
                    pname, value = load_property(property)
                    if pname == "sizeHint":
                        width = value.width()
                        height = value.height()
                    elif pname == "orientation":
                        orient_ = 2 if value == 1 else 1  # 1 Horizontal, 2 Vertical

                    elif pname == "sizeType":
                        # print("Convirtiendo %s a %s" % (p.find("enum").text, value))
                        if (
                            settings.CONFIG.value("ebcomportamiento/spacerLegacy", False)
                            or orient_ == 1
                        ):
                            policy_ = QtWidgets.QSizePolicy.Policy(value)
                        else:
                            policy_ = QtWidgets.QSizePolicy.Policy.Expanding  # Siempre Expanding

                    elif pname == "name":
                        spacer_name = value  # noqa: F841

                if orient_ == 1:
                    hor_policy = policy_
                else:
                    ver_policy = policy_

                # print(
                #    "Nuevo spacer %s (%s,%s,(%s,%s), %s, %s"
                #    % (
                #        spacer_name,
                #        "Horizontal" if orient_ == 1 else "Vertical",
                #        policy_,
                #        width,
                #        height,
                #        hor_policy,
                #        ver_policy,
                #    )
                # )
                new_spacer = QtWidgets.QSpacerItem(width, height, hor_policy, ver_policy)
                if mode == "grid":
                    widget._layout.addItem(new_spacer, row, col, int(row_span), int(col_span))
                else:
                    widget._layout.addItem(new_spacer)
                # print("Spacer %s.%s --> %s" % (spacer_name, new_spacer, widget.objectName()))
            else:
                LOGGER.warning("qt3ui: Unknown layout xml tag", repr(item.tag))

        if widget.layout() is None:
            widget.setLayout(widget._layout)
        # widget._layout.setContentsMargins(1, 1, 1, 1)
        # widget._layout.setSpacing(1)
        # widget._layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)


def load_icon(xml: "ET.Element") -> None:
    """Load Icon from XML."""
    global ICONS

    name = xml.get("name")
    xmldata = xml.find("data")
    if name is None:
        LOGGER.warning("loadIcon: provided xml lacks attr name")
        return
    if xmldata is None:
        LOGGER.warning("loadIcon: provided xml lacks <data>")
        return
    img_format = xmldata.get("format")
    if xmldata.text is None:
        LOGGER.warning("loadIcon: text is empty")
        return

    data = unhexlify(xmldata.text.strip())
    pixmap = QtGui.QPixmap()
    if img_format == "XPM.GZ":
        data = zlib.decompress(data, 15)
        img_format = "XPM"
    pixmap.loadFromData(data, img_format)  # type: ignore [call-overload]
    icon = QtGui.QIcon(pixmap)
    ICONS[name] = icon


def load_variant(xml: ET.Element, widget: Optional[QtCore.QObject] = None) -> Any:
    """Load Variant from XML."""
    for variant in xml:
        return _load_variant(variant, widget)
    raise ValueError("No property in provided XML")


def load_property(xml: ET.Element) -> Tuple[Any, Any]:
    """Load a Qt Property from XML."""
    for variant in xml:
        return (xml.get("name"), _load_variant(variant))
    raise ValueError("No property in provided XML")


def parse_string(value: Any) -> str:
    """Convert x to string."""
    return str(value)


def parse_bool(value: str) -> bool:
    """Convert x to bool."""
    value = value.lower()
    if value[0] in ("t", "1", "on"):
        return True
    elif value[0] in ("f", "0", "off"):
        return False
    else:
        LOGGER.warning("Bool?:", repr(value))

    return False


def _load_variant(variant: ET.Element, widget: Optional[QtCore.QObject] = None) -> Any:
    """Load a variant from XM. Internal."""
    text = variant.text or ""
    text = text.strip()
    if variant.tag == "cstring":
        return text
    elif variant.tag in ["iconset", "pixmap"]:
        global ICONS
        if text in ICONS.keys():

            return ICONS[text]
        else:
            LOGGER.warning("Icon %s not found:", text)
        return
    elif variant.tag == "string":
        return parse_string(text)
    elif variant.tag == "number":
        if text.find(".") >= 0:
            return float(text)
        return int(text)
    elif variant.tag == "bool":
        return parse_bool(text)
    elif variant.tag == "rect":
        rect_ = {}
        for item in variant:
            rect_[item.tag] = int((item.text or "0").strip())
        return QtCore.QRect(rect_["x"], rect_["y"], rect_["width"], rect_["height"])

    elif variant.tag == "sizepolicy":

        policy = QtWidgets.QSizePolicy()
        for item in variant:
            ivalue_policy = int((item.text or "0").strip())
            real_policy: Any = None
            for it_ in policy.Policy:
                if it_.value == ivalue_policy:
                    real_policy = it_
                    break

            if item.tag == "hsizetype":
                policy.setHorizontalPolicy(real_policy)
            elif item.tag == "vsizetype":
                policy.setVerticalPolicy(real_policy)
            elif item.tag == "horstretch":
                policy.setHorizontalStretch(ivalue_policy)
            elif item.tag == "verstretch":
                policy.setVerticalStretch(ivalue_policy)

        return policy

    elif variant.tag == "size":
        p_sz = QtCore.QSize()
        for item in variant:
            ivalue = int((item.text or "0").strip())
            if item.tag == "width":
                p_sz.setWidth(ivalue)
            elif item.tag == "height":
                p_sz.setHeight(ivalue)
        return p_sz
    elif variant.tag == "font":
        p_font = QtGui.QFont()
        for item in variant:
            value = (item.text or "0").strip()
            bool_value: bool = False
            if item.tag not in ("family", "pointsize"):
                bool_value = parse_bool(value)
            try:
                if item.tag == "bold":
                    p_font.setBold(bool_value)
                elif item.tag == "italic":
                    p_font.setItalic(bool_value)
                elif item.tag == "family":
                    p_font.setFamily(value)
                elif item.tag == "pointsize":
                    p_font.setPointSize(int(value))
                else:
                    LOGGER.warning("unknown font style type %s", repr(item.tag))
            except Exception as exc_error:
                LOGGER.warning(exc_error)
        return p_font

    elif variant.tag == "set":
        final = 0
        text = variant.text or "0"

        if text.find("WordBreak|") > -1:
            if widget is not None and hasattr(widget, "setWordWrap"):
                widget.setWordWrap(True)  # type: ignore [attr-defined] # noqa F821
            text = text.replace("WordBreak|", "")

        for item_ in text.split("|"):
            value = getattr(QtCore.Qt, item_, None)
            if value is not None:
                final = final + int(value)

        return QtCore.Qt.AlignmentFlag(final)

    elif variant.tag == "enum":
        libs_2: List[Any] = [
            QtCore.Qt,
            QtCore.Qt.Orientation,
            QtCore.Qt.AlignmentFlag,
            QtWidgets.QSizePolicy.Policy,
            QtWidgets.QFrame,
            QtWidgets.QSizePolicy,
            QtWidgets.QTabWidget,
            QtCore.Qt.FocusPolicy,
            QtWidgets.QFrame.Shadow,
            QtWidgets.QFrame.Shape,
            QtCore.Qt.TextFormat,
            QtWidgets.QTabWidget.TabShape,
            QtWidgets.QLineEdit.EchoMode,
        ]
        for lib in libs_2:
            value = getattr(lib, text, None)
            if value is not None:
                return value
        if text in ["GroupBoxPanel", "LineEditPanel", "ToolBarPanel"]:
            return QtWidgets.QFrame.Shape.StyledPanel
        if text in ("Single", "SingleRow"):
            return QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
        if text == "FollowStyle":
            return "QtWidgets.QTableView {selection-background-color: red;}"
        if text in ("MultiRow", "Multi"):
            return QtWidgets.QAbstractItemView.SelectionMode.MultiSelection
        if text == "Reject":
            return False

        att_found = getattr(widget, text, None)
        if att_found is not None:
            return att_found

    elif variant.tag == "color":
        qcolor = QtGui.QColor()
        red_ = 0
        green_ = 0
        blue_ = 0
        for color in variant:
            if color.text is None:
                continue
            if color.tag == "red":
                red_ = int(color.text.strip())
            elif color.tag == "green":
                green_ = int(color.text.strip())
            elif color.tag == "blue":
                blue_ = int(color.text.strip())

        qcolor.setRgb(red_, green_, blue_)
        return qcolor

    elif variant.tag == "palette":
        pal_ = QtGui.QPalette()
        for state in variant:
            print("FIXME: Procesando palette", state.tag)
            for color in state:
                red_ = 0
                green_ = 0
                blue_ = 0
                for item in color:
                    if item.text is None:
                        continue
                    if item.tag == "red":
                        red_ = int(item.text)
                    elif item.tag == "green":
                        green_ = int(item.text)
                    elif item.tag == "blue":
                        blue_ = int(item.text)

                if state.tag in ("active", "disabled", "inactive", "normal"):
                    pass
                else:
                    LOGGER.warning("Unknown palette state %s", state.tag)
                LOGGER.debug("pallete color: %s %s %s", red_, green_, blue_)

        return pal_

    elif variant.tag == "date":

        year_ = 2000
        month_ = 1
        day_ = 1
        for item_variant in variant:
            if item_variant.text is None:
                continue
            if item_variant.tag == "year":
                year_ = int(item_variant.text)
            elif item_variant.tag == "month":
                month_ = int(item_variant.text)
            elif item_variant.tag == "day":
                day_ = int(item_variant.text)

        return QtCore.QDate(year_, month_, day_)

    if Options.DEBUG_LEVEL > 50:
        LOGGER.warning("qt3ui: Unknown variant: %s --> %s ", repr(widget), ET.tostring(variant))
