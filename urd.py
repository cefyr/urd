#!/usr/bin/env python3

from PyQt4 import QtGui
from PyQt4.QtCore import Qt

from libsyntyche import common

from scene import Scene
from terminal import Terminal

class MainWindow(QtGui.QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Urd')

        layout = QtGui.QVBoxLayout(self)
        common.kill_theming(layout)

        self.scene = Scene()

        view = QtGui.QGraphicsView(self.scene)
        view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        view.setStyleSheet('padding: 6px; background: #222; border: none;')
        layout.addWidget(view)

        self.terminal = Terminal(self)
        layout.addWidget(self.terminal)

        connect_signals(self.scene, self.terminal)

        self.show()

def connect_signals(scene, term):
    connect = (
        (term.add_plotline, scene.add_plotline),
        (term.add_timeslot, scene.add_timeslot),
        (term.insert_plotline, scene.insert_plotline),
        (term.insert_timeslot, scene.insert_timeslot),
        (term.move_plotline, scene.move_plotline),
        (term.move_timeslot, scene.move_timeslot),
        (term.remove_plotline, scene.remove_plotline),
        (term.remove_timeslot, scene.remove_timeslot),
        (scene.error, term.error),
        (scene.print_, term.print_)
    )
    for signal, slot in connect:
        signal.connect(slot)


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
