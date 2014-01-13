
from PyQt4 import QtGui, QtCore


class EventItem():
    def __init__(self, scene, font, brush):
        self.scene = scene
        self.background = QtGui.QGraphicsRectItem(scene=scene)
        self.background.setBrush(QtGui.QBrush(QtGui.QColor('#bbb')))
        self.background.setZValue(-5)
        self.background.hide()

        self.text_widget = QtGui.QGraphicsSimpleTextItem(scene=scene)
        self.text_widget.setFont(font)
        self.text_widget.setBrush(brush)
        self.text_widget.hide()

        self.size = QtCore.QSizeF(0,0)

    def remove(self):
        self.scene.removeItem(self.background)
        self.scene.removeItem(self.text_widget)

    def show(self):
        self.background.show()
        self.text_widget.show()

    def hide(self):
        self.background.hide()
        self.text_widget.hide()
        self.size.scale(0, 0, QtCore.Qt.IgnoreAspectRatio)

    def width(self):
        return self.size.width()

    def height(self):
        return self.size.height()

    def set_size(self, newsize):
        self.size.scale(newsize, QtCore.Qt.IgnoreAspectRatio)

    def set_pos(self, x, y):
        w, h = self.width(), self.height()
        self.background.setRect(x-w/2-4, y-h/2-2, w+8, h+4)
        self.text_widget.setPos(x-w/2, y-h/2)

    def set_text(self, text):
        self.text_widget.setText(text)

    def set_font(self, font):
        self.text_widget.setFont(font)

    def text(self):
        return self.text_widget.text()
