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

        self.force_quit_flag = False

        layout = QtGui.QVBoxLayout(self)
        common.kill_theming(layout)

        scene_container = QtGui.QScrollArea(self)
        layout.addWidget(scene_container, stretch=1)

        self.scene = Scene()

        scene_container.setWidget(self.scene)

        self.terminal = Terminal(self)
        layout.addWidget(self.terminal)

        self.connect_signals(self.scene, self.terminal)

        self.show()

    # Override
    # def closeEvent(self, event):
    #     if not self.scene.is_modified() or self.force_quit_flag:
    #         event.accept()
    #     else:
    #         self.terminal.error('Unsaved changes! Force quit with q! or save first.')
    #         event.ignore()

    # def quit(self, force):
    #     if force:
    #         self.force_quit_flag = True
    #         self.close()
    #     else:
    #         self.force_quit_flag = False
    #         self.close()

    def connect_signals(self, scene, term):
        connect = (
            (term.add_plotline, scene.add_plotline),
            (term.add_timeslot, scene.add_timeslot),
            (term.insert_plotline, scene.insert_plotline),
            (term.insert_timeslot, scene.insert_timeslot),
            (term.move_plotline, scene.move_plotline),
            (term.move_timeslot, scene.move_timeslot),
            (term.remove_plotline, scene.remove_plotline),
            (term.remove_timeslot, scene.remove_timeslot),
            (term.edit_cell, scene.edit_cell),
            (term.clear_cell, scene.clear_cell),
            (term.undo, scene.undo),
            (term.set_time_orientation, scene.set_time_orientation),

            # Terminal actions
            (scene.prompt_sig, term.prompt),
            (scene.error_sig, term.error),
            (scene.print_, term.print_),

            # File operations
            (term.request_new_file, scene.request_new_file),
            (term.request_save_file, scene.request_save_file),
            (term.request_open_file, scene.request_open_file),
            # (term.request_quit, self.quit)
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
