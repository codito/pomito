# -*- coding: utf-8 -*-
"""
Steps to compile resources for Qt
"""
import sys
from os import path

def get_pyqt_install_root():
    """Gets pyqt install path in windows environment."""
    pyqt_install_root = None
    if sys.platform == "win32":
        python_root = path.split(sys.executable)[0]
        pyqt_install_root = path.join(python_root, "Lib\\site-packages\\PyQt5")
    return pyqt_install_root


def build_qt():
    """Build Qt resource files."""
    import subprocess

    uic = "pyuic5"
    rcc = "pyrcc5"
    # lupdate = "pylupdate5"
    # if sys.platform.startswith("win"):
        # pyqt_windows_root = get_pyqt_install_root()
        # uic = path.join(pyqt_windows_root, uic + ".bat")
        # rcc = path.join(pyqt_windows_root, rcc)
        # lupdate = path.join(pyqt_windows_root, lupdate)

    subprocess.check_call([uic, "data/qt/timer.ui", "--from-imports", "-o", "pomito/plugins/ui/qt_timer.py"])
    subprocess.check_call([uic, "data/qt/task.ui", "--from-imports", "-o", "pomito/plugins/ui/qt_task.py"])
    subprocess.check_call([uic, "data/qt/interrupt.ui", "--from-imports", "-o", "pomito/plugins/ui/qt_interrupt.py"])
    subprocess.check_call([rcc, "data/qt/pomito.qrc", "-o", "pomito/plugins/ui/pomito_rc.py"])
    return

build_qt()
