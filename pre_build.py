# -*- coding: utf-8 -*-
"""
Steps to compile resources for Qt
"""


def build_qt():
    import subprocess
    import sys
    from os import path

    pyqt_windows_root = "C:\Python33\Lib\site-packages\PyQt5"
    uic = "pyuic5"
    rcc = "pyrcc5"
    lupdate = "pylupdate5"
    if sys.platform.startswith("win"):
        uic = path.join(pyqt_windows_root, uic + ".bat")
        rcc = path.join(pyqt_windows_root, rcc)
        lupdate = path.join(pyqt_windows_root, lupdate)

    subprocess.check_call([uic, "data/qt/timer.ui", "--from-imports", "-o", "pomito/plugins/ui/qt_timer.py"])
    subprocess.check_call([uic, "data/qt/task.ui", "--from-imports", "-o", "pomito/plugins/ui/qt_task.py"])
    subprocess.check_call([uic, "data/qt/interrupt.ui", "--from-imports", "-o", "pomito/plugins/ui/qt_interrupt.py"])
    subprocess.check_call([rcc, "data/qt/pomito.qrc", "-o", "pomito/plugins/ui/pomito_rc.py"])
    return

build_qt()
