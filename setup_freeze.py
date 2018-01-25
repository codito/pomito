#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Freeze script for pomito."""

import os
import sys

import setup
import cx_Freeze
from setuptools import find_packages
from pre_build import build_qt, get_pyqt_install_root


# Build qt related resources
build_qt()

# Setup cx_Freeze packaging
# pylint: disable=invalid-name
base = None
includefiles = []
if sys.platform == "win32":
    from os import path
    pyqt_windows_root = get_pyqt_install_root()
    includefiles = [
        (path.join(pyqt_windows_root, "qt\\plugins\\platforms\\qwindows.dll"),
         "platforms\\qwindows.dll"),
        ("pomito\\plugins\\ui\\qt\\wintaskbar.tlb", "wintaskbar.tlb"),
    ]
    base = "Win32GUI"

includefiles += [
    ("docs/sample_config.ini", "docs/sample_config.ini"),
    ("docs/sample_todo.txt", "docs/sample_todo.txt"),
]

executables = [cx_Freeze.Executable("pomito.py",
                                    base=base,
                                    icon="data/qt/pomito_64x64.ico")]
buildOptions = dict(packages=[], excludes=[],
                    includes=["atexit", "sip", "idna.idnadata"],
                    include_files=includefiles,
                    zip_include_packages=["*"],
                    zip_exclude_packages=[],
                    optimize=2
                    )
setup_options = dict(build_exe=buildOptions)


# Load the package"s __version__.py module as a dictionary.
about = {}
about["__version__"] = '.'.join(map(str, setup.VERSION))

cx_Freeze.setup(
    name=setup.NAME,
    version=about["__version__"],
    description=setup.DESCRIPTION,
    author=setup.AUTHOR,
    author_email=setup.EMAIL,
    url=setup.URL,
    packages=find_packages(exclude=("tests",)),
    scripts=["pomito.py"],
    executables=executables,

    options=setup_options,
    include_package_data=True,
    license="MIT",
)
