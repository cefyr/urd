#!/usr/bin/env python3

from PyQt4 import QtGui
from PyQt4.QtCore import Qt

from libsyntyche import common

from scene import Scene

class MainWindow(QtGui.QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Urd')

        layout = QtGui.QVBoxLayout(self)
        common.kill_theming(layout)

        scene = Scene()

        view = QtGui.QGraphicsView(scene)
        view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        view.setStyleSheet('border: 0px')
        layout.addWidget(view)

        self.show()

def create_scene():
    scene = QtGui.QGraphicsScene()
    scene.setBackgroundBrush(QtGui.QColor('#222'))



    pen = QtGui.QPen(QtGui.QBrush(QtGui.QColor('red')), 10)
    scene.addLine(0,20,100,20,pen)
    scene.addLine(0,100,100,100,pen)
    pen.setColor(QtGui.QColor('green'))
    scene.addLine(50,0,50,150,pen)
    return scene



def main():
    import sys
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('profile', nargs='?')
    # args = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    app.setActiveWindow(window)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
