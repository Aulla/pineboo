"""Main setup script."""

import setuptools  # type: ignore
import pathlib
import subprocess
from pineboolib import application


with open("requirements.txt") as f:
    required = f.read().splitlines()

prj_ = application.PROJECT
prj_.load_version()
version_ = application.PINEBOO_VER
# Create/Update translations

languages = ["es", "en", "ca", "de", "fr", "gl", "it", "pt"]
lang_path = pathlib.Path("pineboolib")
files = [str(fil) for fil in lang_path.glob("**/*.py")]
exclude_uis = [
    "pineboolib/application/packager/tests/fixtures/principal/forms/agentes.ui",
    "pineboolib/application/packager/tests/fixtures/principal/forms/flfactppal.ui",
    "pineboolib/application/parsers/parser_ui/tests/fixtures/main_form_qt3.ui",
    "pineboolib/application/parsers/parser_ui/tests/fixtures/form_record_qt3.ui",
    "pineboolib/fllegacy/forms/FLWidgetReportViewer.ui",
]
files.extend([str(fil) for fil in lang_path.glob("**/*.ui")])
for exclude in exclude_uis:
    files.remove(exclude)

for lang in languages:
    ts_file = pathlib.Path("pineboolib/system_module/translations/sys.%s.ts" % lang).absolute()
    if subprocess.call(["pylupdate6", "-ts", ts_file, *files]):
        raise Exception("Error updating %s file!" % ts_file)


with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pineboo",
    version=version_,
    author="David Martínez Martí, José A. Fernández Fernández",
    author_email="deavidsedice@gmail.com, aullasistemas@gmail.com",
    description="ERP replacement for Eneboo written in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deavid/pineboo",
    packages=setuptools.find_packages(),
    package_data={
        "pineboolib": ["py.typed"],
        "pineboolib.application.staticloader.ui": ["*.ui"],
        "pineboolib.core.fonts.Noto_Sans": ["*"],
        "pineboolib.core.images.icono_pi": ["*"],
        "pineboolib.core.images.icons": ["*"],
        "pineboolib.core.images.splashscreen": ["*"],
        "pineboolib.system_module": ["*"],
        "pineboolib.system_module.forms": ["*.ui"],
        "pineboolib.system_module.queries": ["*.qry"],
        "pineboolib.system_module.tables": ["*.mtd"],
        "pineboolib.system_module.translations": ["*.ts"],
        "pineboolib.loader.dlgconnect": ["*.ui"],
        "pineboolib.plugins.dgi.dgi_qt.dgi_objects.dlg_about": ["*.ui"],
        "pineboolib.plugins.mainform.eneboo": ["*.ui"],
        "pineboolib.plugins.mainform.eneboo_mdi": ["*.ui"],
        "pineboolib.fllegacy.forms": ["*.ui"],
    },
    install_requires=required,
    keywords="erp pineboo eneboo accounting sales warehouse",
    python_requires=">=3.6.9",
    entry_points={
        "console_scripts": [
            "pineboo-parse=pineboolib.application.parsers.parser_qsa.postparse:main",
            "pineboo-pyconvert=pineboolib.application.parsers.parser_qsa.pyconvert:main",
            "pineboo-core=pineboolib.loader.main:startup_no_x",
            "pineboo-packager=pineboolib.application.packager.pnpackager:main",
            "pineboo-daemon=pineboolib.application.utils.service:main",
            "pineboo=pineboolib.loader.main:startup",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Environment :: X11 Applications :: Qt",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Typing :: Typed",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Natural Language :: Spanish",
        "Operating System :: OS Independent",
    ],
)
