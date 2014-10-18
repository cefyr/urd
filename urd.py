#!/usr/bin/env python3

import os.path

from PyQt4 import QtGui
from PyQt4.QtCore import Qt

from libsyntyche import common

from scene import Scene
from terminal import Terminal

class MainWindow(QtGui.QFrame):
    def __init__(self, file_to_open=''):
        super().__init__()
        self.setWindowTitle('New file')

        self.force_quit_flag = False

        self.config = read_config()
        self.setStyleSheet('background: '+self.config['theme']['background'])

        layout = QtGui.QVBoxLayout(self)
        common.kill_theming(layout)

        scene_container = QtGui.QScrollArea(self)
        layout.addWidget(scene_container, stretch=1)

        self.scene = Scene(self.config,
                scene_container.horizontalScrollBar().value,
                scene_container.verticalScrollBar().value)

        scene_container.setWidget(self.scene)

        self.terminal = Terminal(self, lambda: self.scene.file_path)
        layout.addWidget(self.terminal)

        self.connect_signals(self.scene, self.terminal)

        common.set_hotkey('Escape', self, self.terminal.toggle)
        common.set_hotkey('Ctrl+N', self, self.scene.request_new_file)
        common.set_hotkey('Ctrl+O', self, lambda:self.terminal.prompt('o '))
        common.set_hotkey('Ctrl+S', self, self.scene.request_save_file)
        common.set_hotkey('Ctrl+Shift+S', self,
                          lambda:self.terminal.prompt('s '))

        if file_to_open:
            self.scene.open_file(file_to_open)

        self.show()

    # Override
    def closeEvent(self, event):
        if not self.scene.is_modified() or self.force_quit_flag:
            event.accept()
        else:
            self.terminal.error('Unsaved changes! Force quit with q! or save first.')
            event.ignore()

    def quit(self, force):
        if force:
            self.force_quit_flag = True
            self.close()
        else:
            self.force_quit_flag = False
            self.close()

    def connect_signals(self, scene, term):
        connect = (
            (term.add_plotline, scene.add_plotline),
            (term.add_timeslot, scene.add_timeslot),
            (term.insert_plotline, scene.insert_plotline),
            (term.insert_timeslot, scene.insert_timeslot),
            (term.move_plotline, scene.move_plotline),
            (term.move_timeslot, scene.move_timeslot),
            (term.copy_plotline, scene.copy_plotline),
            (term.copy_timeslot, scene.copy_timeslot),
            (term.remove_plotline, scene.remove_plotline),
            (term.remove_timeslot, scene.remove_timeslot),
            (term.move_cell, scene.move_cell),
            (term.copy_cell, scene.copy_cell),
            (term.edit_cell, scene.edit_cell),
            (term.clear_cell, scene.clear_cell),
            (term.undo, scene.undo),
            (term.set_time_orientation, scene.set_time_orientation),
            (scene.window_title_changed, self.setWindowTitle),

            # Terminal actions
            (scene.prompt_sig, term.prompt),
            (scene.error_sig, term.error),
            (scene.print_, term.print_),
            (term.give_up_focus, scene.setFocus),

            # File operations
            (term.request_new_file, scene.request_new_file),
            (term.request_save_file, scene.request_save_file),
            (term.request_open_file, scene.request_open_file),
            (term.request_quit, self.quit)
        )
        for signal, slot in connect:
            signal.connect(slot)


def read_config():
    config_file = os.path.join(os.getenv('HOME'), '.config', 'urd', 'urd.conf')
    common.make_sure_config_exists(config_file,
                                   common.local_path('default_config.json'))
    return common.read_json(config_file)


def main():
    import argparse, subprocess, sys
    parser = argparse.ArgumentParser()

    def valid_file(fname):
        if os.path.isfile(fname):
            return fname
        parser.error('File does not exist: {}'.format(fname))

    parser.add_argument('files', nargs='*', type=valid_file)
    args = parser.parse_args()

    app = QtGui.QApplication([])
    if not args.files:
        window = MainWindow()
    else:
        window = MainWindow(file_to_open=args.files[0])
        for f in args.files[1:]:
            subprocess.Popen([sys.executable, sys.argv[0], f.encode('utf-8')])

    app.setActiveWindow(window)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
