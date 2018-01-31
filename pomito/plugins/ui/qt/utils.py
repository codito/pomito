# -*- coding: utf-8 -*-
"""Utilities for Qt integration."""

from PyQt5 import QtCore, QtGui


def get_elided_text(rect, font, text):
    """Get elided text to fit given rectangle.

    Args:
        rect: Rectangle which will contain the text. Type: QtCore.QRect
        font: Font used to render text. Type: QtCore.QFont
        text: String to render
    """
    textLayout = QtGui.QTextLayout(text, font)
    metrics = QtGui.QFontMetrics(font)
    textLayout.beginLayout()
    line = textLayout.createLine()
    totalWidth = 0
    totalHeight = 0
    while line.isValid():
        line.setLineWidth(rect.width())
        rectCovered = line.naturalTextRect()
        totalWidth += rectCovered.width()
        if totalHeight + rectCovered.width() > rect.height():
            break
        else:
            totalHeight += rectCovered.height()

        line = textLayout.createLine()
    textLayout.endLayout()

    # XXX are we calculating the width correctly?
    return metrics.elidedText(text, QtCore.Qt.ElideRight, totalWidth + rect.width())
