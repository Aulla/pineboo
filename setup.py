"""Main setup script."""

import setuptools  # type: ignore
import pathlib
import subprocess
from pineboolib import application

prj_ = application.project
prj_.load_version()
version_ = prj_.version[prj_.version.find(" v") + 2 :]
# Create/Update translations

languages = ["es", "en", "ca", "de", "eu", "fr", "gl", "it", "pt"]
lang_path = pathlib.Path("pineboolib")
py_files = lang_path.glob("**/*.py")
ts_files = []
for lang in languages:
    ts_files.append(
        pathlib.Path("pineboolib/system_module/translations/sys.%s.ts" % lang).absolute()
    )

ret = subprocess.call(["pylupdate5", *py_files, "-ts", *ts_files])
if ret != 0:
    raise Exception("Error updating .ts files!")

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
    },
    keywords="erp pineboo eneboo accounting sales warehouse",
    python_requires="~=3.6",
    entry_points={
        "console_scripts": [
            "pineboo-parse=pineboolib.application.parsers.qsaparser.postparse:main",
            "pineboo-pyconvert=pineboolib.application.parsers.qsaparser.pyconvert:main",
            "pineboo-core=pineboolib.loader.main:startup_no_X",
            "pineboo=pineboolib.loader.main:startup",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
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
