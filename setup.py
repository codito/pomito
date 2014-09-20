"""Setup script for pomito."""

import sys
from setuptools import setup

from cx_Freeze import setup, Executable

from pre_build import build_qt, get_pyqt_install_root

# Build qt related resources
build_qt()

# Setup cx_freeze packaging
# pylint: disable=invalid-name
base = None
includefiles = None
if sys.platform == "win32":
    from os import path
    pyqt_windows_root = get_pyqt_install_root()
    includefiles = [
        (path.join(pyqt_windows_root, "plugins\\platforms\\qwindows.dll"),
         "platforms\\qwindows.dll"),
        ("pomito\\plugins\\ui\\wintaskbar.tlb", "wintaskbar.tlb"),
    ]

includefiles += [
    ("docs\\sample_config.ini", "docs\\sample_config.ini"),
    ("docs\\sample_todo.txt", "docs\\sample_todo.txt"),
]

buildOptions = dict(packages=[], excludes=[],
                    includes=["atexit", "sip",],
                    include_files=includefiles)

executables = [Executable('pomito.py', base=base)]

setup(
    name='Pomito',
    version='0.1.0',
    author='Arun Mahapatra',
    packages=['pomito'],
    scripts=['pomito.py'],
    url='https://www.github.com/codito/pomito',
    license='LICENSE',
    description='Simple pomodoro timer with support for tasks and hooks',
    long_description=open('README.md').read(),
    install_requires=[
        "pywin32",
        "peewee",
        "pyrtm",
        "blinker",
        "comtypes",
        "cx-freeze",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
    test_suite='py.test',
    tests_require=[
        "pyfakefs",
        "pytest",
        "pytest-cov",
        "sure",
    ],
    options=dict(build_exe=buildOptions),
    executables=executables
)
