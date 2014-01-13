import os.path
import re

from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSignal

from libsyntyche.terminal import GenericTerminalInputBox, GenericTerminalOutputBox, GenericTerminal


class Terminal(GenericTerminal):

    add_plotline = pyqtSignal(str)
    add_timeslot = pyqtSignal(str)
    insert_plotline = pyqtSignal(int, str)
    insert_timeslot = pyqtSignal(int, str)
    move_plotline = pyqtSignal(int, str)
    move_timeslot = pyqtSignal(int, str)
    remove_plotline = pyqtSignal(int)
    remove_timeslot = pyqtSignal(int)
    edit_cell = pyqtSignal(int, int, str)
    clear_cell = pyqtSignal(int, int)


    def __init__(self, parent):
        super().__init__(parent, GenericTerminalInputBox, GenericTerminalOutputBox)

        self.commands = {
            '?': (self.cmd_help, 'List commands or help for [command]'),
            'a': (self.cmd_add, 'Add plotline/timeslot (a[pt][NAME])'),
            'i': (self.cmd_insert, 'Insert plotline/timeslot (i[pt][POS] [NAME])'),
            'm': (self.cmd_move, 'Move plotline/timeslot (m[pt][OLDPOS] [NEWPOS])'),
            'r': (self.cmd_remove, 'Remove plotline/timeslot (r[pt][POS])'),
            'e': (self.cmd_edit, 'Edit cell (e[COL] [ROW] [TEXT])'),
            'c': (self.cmd_clear, 'Clear cell (c[COL] [ROW])'),
            'q': (self.cmd_quit, 'Quit')
        }



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
        rx = re.match(r'([pt])(\d+) +(.+)', arg)
        if not rx:
            self.error('Invalid insert command')
        elif rx.group(1) == 'p':
            self.insert_plotline.emit(int(rx.group(2)), rx.group(3))
        elif rx.group(1) == 't':
            self.insert_timeslot.emit(int(rx.group(2)), rx.group(3))

    def cmd_move(self, arg):
        rx = re.match(r'([pt])([1-9]\d*) *( +[1-9]\d*|\+|-)', arg)
        if not rx:
            self.error('Invalid move command')
        elif rx.group(1) == 'p':
            self.move_plotline.emit(int(rx.group(2)), rx.group(3).strip())
        elif rx.group(1) == 't':
            self.move_timeslot.emit(int(rx.group(2)), rx.group(3).strip())

    def cmd_remove(self, arg):
        rx = re.match(r'([pt])(\d+)', arg)
        if not rx:
            self.error('Invalid remove command')
        elif rx.group(1) == 'p':
            self.remove_plotline.emit(int(rx.group(2)))
        elif rx.group(1) == 't':
            self.remove_timeslot.emit(int(rx.group(2)))

    def cmd_edit(self, arg):
        rx = re.match(r'(\d+) +(\d+)(\s+\S.*)?', arg)
        if not rx:
            self.error('Invalid edit command')
        elif not rx.group(3):
            self.edit_cell.emit(int(rx.group(1)), int(rx.group(2)), '')
        else:
            self.edit_cell.emit(int(rx.group(1)), int(rx.group(2)), rx.group(3).strip())

    def cmd_clear(self, arg):
        rx = re.match(r'(\d+) +(\d+)$', arg)
        if not rx:
            self.error('Invalid clear command')
        else:
            self.clear_cell.emit(int(rx.group(1)), int(rx.group(2)))

    def cmd_quit(self, arg):
        pass
        # self.request_quit.emit(arg.startswith('!'))

