#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for pomito."""

import io
import os
import sys

from shutil import rmtree
from setuptools import Command, find_packages, setup

build_version_minor = "0"
if os.getenv("APPVEYOR_BUILD"):
    build_version_minor = int(os.getenv("APPVEYOR_BUILD_NUMBER")) % 100
elif os.getenv("TRAVIS_BUILD"):
    build_version_minor = int(os.getenv("TRAVIS_BUILD_NUMBER")) % 100

# Package meta-data.
NAME = "pomito"
DESCRIPTION = "Simple pomodoro timer with support for tasks and hooks"
URL = "https://github.com/codito/pomito"
EMAIL = "arun@codito.in"
AUTHOR = "Arun Mahapatra"
VERSION = (0, 2, build_version_minor)

# Dependencies required for execution
REQUIRED = [
    "asana",
    "blinker",
    "click>=6.7",
    "comtypes==1.1.3post2",
    "cx-freeze",
    # "pywin32",
    "peewee",
    "pyrtm",
    "pyqtkeybind",
    "PyQt5",
    "py-trello",
]

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if "README.md" is present in your MANIFEST.in file!
with io.open(os.path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

# Load the package"s __version__.py module as a dictionary.
about = {}
about["__version__"] = '.'.join(map(str, VERSION))


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Print things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        """Initialize setup options."""
        pass

    def finalize_options(self):
        """Finalize setup options."""
        pass

    def run(self):
        """Run the setup command."""
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal"
                  .format(sys.executable))

        self.status("Uploading the package to PyPi via Twine…")
        os.system("twine upload dist/*")

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=("tests",)),
    scripts=["pomito.py"],

    install_requires=REQUIRED,
    include_package_data=True,
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"
        "Development Status :: 3 - Alpha",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
    # $ setup.py publish support.
    cmdclass={
        "upload": UploadCommand,
    },
)
