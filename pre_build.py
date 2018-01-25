# -*- coding: utf-8 -*-
"""Steps to compile resources for Qt."""
import importlib.util


def get_pyqt_install_root():
    """Get pyqt install path."""
    pyqt = ""
    try:
        pyqt = importlib.util.find_spec('PyQt5').submodule_search_locations[0]
    except Exception:
        # Don't do anything, likely all dependencies are not available yet
        pass
    return pyqt


def build_qt():
    """Build Qt resource files."""
    import subprocess

    uic = "pyuic5"
    rcc = "pyrcc5"
    uic_files = [("data/qt/timer.ui", "pomito/plugins/ui/qt/qt_timer.py"),
                 ("data/qt/task.ui", "pomito/plugins/ui/qt/qt_task.py"),
                 ("data/qt/interrupt.ui", "pomito/plugins/ui/qt/qt_interrupt.py")]
    rcc_files = [("data/qt/pomito.qrc", "pomito/plugins/ui/qt/pomito_rc.py")]

    for f in uic_files:
        subprocess.check_call([uic, f[0], "--from-imports", "-o", f[1]])

    for f in rcc_files:
        subprocess.check_call([rcc, f[0], "-o", f[1]])
    return


build_qt()
