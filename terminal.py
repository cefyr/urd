import os
import os.path
import re

from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSignal

from libsyntyche.terminal import GenericTerminalInputBox, GenericTerminalOutputBox, GenericTerminal


class Terminal(GenericTerminal):
    request_new_file = pyqtSignal(bool)
    request_open_file = pyqtSignal(str, bool)
    request_save_file = pyqtSignal(str, bool)
    request_quit = pyqtSignal(bool)

    add_plotline = pyqtSignal(str)
    add_timeslot = pyqtSignal(str)
    insert_plotline = pyqtSignal(int, str)
    insert_timeslot = pyqtSignal(int, str)
    move_plotline = pyqtSignal(int, str)
    move_timeslot = pyqtSignal(int, str)
    copy_plotline = pyqtSignal(int, str)
    copy_timeslot = pyqtSignal(int, str)
    remove_plotline = pyqtSignal(int)
    remove_timeslot = pyqtSignal(int)
    move_cell = pyqtSignal(int, int, int, int)
    copy_cell = pyqtSignal(int, int, int, int)
    edit_cell = pyqtSignal(int, int, str)
    clear_cell = pyqtSignal(int, int)

    undo = pyqtSignal(str)
    set_time_orientation = pyqtSignal(str)

    give_up_focus = pyqtSignal()


    def __init__(self, parent, get_filepath):
        super().__init__(parent, GenericTerminalInputBox,
                         GenericTerminalOutputBox)

        self.get_filepath = get_filepath

        self.commands = {
            '?': (self.cmd_help, 'List commands or help for [command]'),
            'a': (self.cmd_add, 'Add plotline/timeslot (a[pt][NAME])'),
            'i': (self.cmd_insert, 'Insert plotline/timeslot (i[pt][POS] [NAME])'),
            'm': (self.cmd_move, 'Move plotline/timeslot (m[cpt][OLD] [NEW])'),
            'r': (self.cmd_remove, 'Remove plotline/timeslot (r[pt][POS])'),
            'c': (self.cmd_copy, 'Copy cell/plotline/timeslot (c[cpt][OLD] [NEW])'),
            'e': (self.cmd_edit_cell, 'Edit cell (e[COL] [ROW] [TEXT])'),
            'd': (self.cmd_clear_cell, 'Clear cell (c[COL] [ROW])'),
            'u': (self.undo, 'Undo'),
            't': (self.set_time_orientation, 'Time orientation (t[hv])'),
            'o': (self.cmd_open, 'Open [file]'),
            'n': (self.cmd_new, 'Open new file'),
            's': (self.cmd_save, 'Save (as) [file]'),
            'q': (self.cmd_quit, 'Quit')
        }

        self.hide()

    def show(self):
        super().show()
        self.input_term.setFocus()

    def toggle(self):
        if self.input_term.hasFocus():
            self.give_up_focus.emit()
            self.hide()
        else:
            self.show()


    # ==== Autocomplete ========================== #

    def autocomplete(self):
        """
        Main autocomplete functions.
        Is called whenever tab is pressed.
        """
        text = self.input_term.text()
        rx = re.match(r'([os]!?)\s*(.*)', text)
        if not rx:
            return
        cmdprefix, ac_text = rx.groups()

        # Autocomplete with the working directory if the line is empty
        if not ac_text:
            wd = os.path.abspath(self.get_filepath())
            if not os.path.isdir(wd):
                wd = os.path.dirname(wd)
            self.prompt(cmdprefix + ' ' + wd + os.path.sep)
            return

        autocompleted_text = self.run_autocompletion(ac_text)
        self.prompt(cmdprefix + ' ' + autocompleted_text)


    def get_ac_suggestions(self, path):
        """
        Return a list of all possible paths that starts with the
        provided path.
        All directories are suffixed with a / or \ depending on os.
        """
        dirpath, namepart = os.path.split(path)
        if not os.path.isdir(dirpath):
            return []
        suggestions = [os.path.join(dirpath, p)
                       for p in sorted(os.listdir(dirpath))
                       if p.lower().startswith(namepart.lower())]
        return [p + (os.path.sep*os.path.isdir(p)) for p in suggestions]


    # ==== Commands ============================== #

    def cmd_add(self, arg):
        name = arg[1:].strip()
        if not name:
            self.error('No name provided')
        elif arg.startswith('p'):
            self.add_plotline.emit(name)
        elif arg.startswith('t'):
            self.add_timeslot.emit(name)
        else:
            self.error('Add either plotline (p) or timeslot (t)')

    def cmd_insert(self, arg):
        rx = re.match(r'([pt]) (\d+) +(.+)', arg)
        if not rx:
            self.error('Invalid insert command')
        elif rx.group(1) == 'p':
            self.insert_plotline.emit(int(rx.group(2)), rx.group(3))
        elif rx.group(1) == 't':
            self.insert_timeslot.emit(int(rx.group(2)), rx.group(3))

    def cmd_move(self, arg):
        rx = re.match(r'([pt]) ([1-9]\d*) *( +[1-9]\d*|\+|-)', arg)
        rxc = re.match(r'c ([1-9]\d*) +([1-9]\d*) +([1-9]\d*) +([1-9]\d*)', arg)
        if not rx and not rxc:
            self.error('Invalid move command')
        elif rx:
            if rx.group(1) == 'p':
                self.move_plotline.emit(int(rx.group(2)), rx.group(3).strip())
            elif rx.group(1) == 't':
                self.move_timeslot.emit(int(rx.group(2)), rx.group(3).strip())
        else:
            self.move_cell.emit(*map(int, rxc.groups()))

    def cmd_copy(self, arg):
        rx = re.match(r'([pt]) ([1-9]\d*) *( +[1-9]\d*|\+|-)', arg)
        rxc = re.match(r'([1-9]\d*) +([1-9]\d*) +([1-9]\d*) +([1-9]\d*)', arg)
        if not rx and not rxc:
            self.error('Invalid copy command')
        elif rx:
            if rx.group(1) == 'p':
                self.copy_plotline.emit(int(rx.group(2)), rx.group(3).strip())
            elif rx.group(1) == 't':
                self.copy_timeslot.emit(int(rx.group(2)), rx.group(3).strip())
        else:
            self.copy_cell.emit(*map(int, rxc.groups()))

    def cmd_remove(self, arg):
        rx = re.match(r'([pt]) (\d+)', arg)
        if not rx:
            self.error('Invalid remove command')
        elif rx.group(1) == 'p':
            self.remove_plotline.emit(int(rx.group(2)))
        elif rx.group(1) == 't':
            self.remove_timeslot.emit(int(rx.group(2)))

    def cmd_edit_cell(self, arg):
        rx = re.match(r'(\d+) +(\d+)(\s+\S.*)?', arg)
        if not rx:
            self.error('Invalid edit command')
        elif not rx.group(3):
            self.edit_cell.emit(int(rx.group(1)), int(rx.group(2)), '')
        else:
            self.edit_cell.emit(int(rx.group(1)), int(rx.group(2)),
                                rx.group(3).strip())

    def cmd_clear_cell(self, arg):
        rx = re.match(r'(\d+) +(\d+)$', arg)
        if not rx:
            self.error('Invalid clear command')
        else:
            self.clear_cell.emit(int(rx.group(1)), int(rx.group(2)))

    def cmd_open(self, arg):
        fname = arg.lstrip('!').lstrip()
        self.request_open_file.emit(fname, arg.startswith('!'))

    def cmd_new(self, arg):
        self.request_new_file.emit(arg.startswith('!'))

    def cmd_save(self, arg):
        fname = arg.lstrip('!').lstrip()
        self.request_save_file.emit(fname, arg.startswith('!'))

    def cmd_quit(self, arg):
        self.request_quit.emit(arg.startswith('!'))

