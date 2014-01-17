#!/usr/bin/env python3

import csv

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QBrush, QColor, QPen
from PyQt4.QtCore import pyqtSignal, Qt

from libsyntyche.filehandling import FileHandler

from matrix import Matrix





class Scene(QtGui.QWidget, FileHandler):
    print_ = pyqtSignal(str)
    error_sig = pyqtSignal(str)
    prompt_sig = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.horizontal_time = False
        self.modified_flag = False
        self.file_path = ''

        self.grid = Matrix()
        self.undo_stack = []

        font = QtGui.QFont('Serif', 10)
        boldfont = QtGui.QFont('Serif', 10, weight=QtGui.QFont.Bold)
        self.font_data = {'def': (font, QtGui.QFontMetrics(font)),
                          'bold': (boldfont, QtGui.QFontMetrics(boldfont))}

        # DEBUG
        self.insert_plotline(1, "This function does not handle the newline character (\\n), as it cannot break text into multiple lines, and it cannot display the newline character. Use the QPainter.drawText() overload that takes a rectangle instead if you want to draw multiple lines of text with the newline character, or if you want the text to be wrapped.")
        self.add_timeslot("HEI")
        self.add_timeslot("HE2")
        self.add_timeslot("HE3")
        self.add_timeslot("HE4")
        self.add_timeslot("HE5")
        self.remove_timeslot(3)

        self.add_timeslot("neee")
        self.edit_cell(1,1,"VA?\nHE\n \nHEHE")
        # self.move_timeslot(8,0)
        # END DEBUG

        self.draw_scene()


    def paintEvent(self, ev):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0,0,self.scene_image)

    def draw_scene(self):
        border = 24
        row_padding, col_padding = 20, 20
        row_heights = [max([x[1][1] for x in self.grid.row_items(row) if x[0]] + [0]) + row_padding
                       for row in range(self.grid.count_rows())]
        col_widths = [max([x[1][0] for x in self.grid.col_items(col) if x[0]] + [0]) + col_padding
                      for col in range(self.grid.count_cols())]

        width = sum(col_widths) + border
        height = sum(row_heights) + border
        self.scene_image = QtGui.QPixmap(width, height)

        # Begin paint
        self.scene_image.fill(QColor('#666'))
        painter = QtGui.QPainter(self.scene_image)
        painter.setFont(self.font_data['def'][0])

        # Draw header lines
        hy = int(border + row_heights[0])
        vx = int(border + col_widths[0])
        painter.drawLine(0, hy, border + sum(col_widths), hy)
        painter.drawLine(vx, 0, vx, border + sum(row_heights))

        # Draw border numbers #TODO: fix the offsets
        for n, rh in list(enumerate(row_heights))[1:]:
            painter.drawText(4, border + sum(row_heights[:n]) + rh/2 + 5, str(n))
        for n, cw in list(enumerate(col_widths))[1:]:
            painter.drawText(border + sum(col_widths[:n]) + cw/2 - 5, 16, str(n))

        # Draw plotline lines
        for n, size in enumerate((col_widths, row_heights)[self.horizontal_time]):
            if n == 0: continue
            if self.horizontal_time:
                x, y = col_widths[0]/2, sum(row_heights[:n]) + size/2 - 5
                w, h = sum(col_widths), 10
            else:
                x, y = sum(col_widths[:n]) + size/2 - 5, row_heights[0]/2
                w, h = 10, sum(row_heights)
            painter.fillRect(border + x, border + y, w, h, QColor('black'))

        # Draw cells
        for r in range(self.grid.count_rows()):
            for c in range(self.grid.count_cols()):
                text, size = self.grid.item(c,r)
                if not text: continue
                if c == 0 or r == 0:
                    painter.setFont(self.font_data['bold'][0])
                else:
                    painter.setFont(self.font_data['def'][0])
                x = border + sum(col_widths[:c]) + col_widths[c]/2 - size[0]/2
                y = border + sum(row_heights[:r]) + row_heights[r]/2 - size[1]/2
                painter.fillRect(x-2, y-2, size[0]+4, size[1]+4, QColor('#ccc'))
                painter.drawRect(x-3, y-3, size[0]+5, size[1]+5)
                painter.drawText(x, y, size[0], size[1], Qt.TextWordWrap, text)

        painter.end()

        self.resize(width, height)
        self.update()


    def prompt(self, text):
        self.prompt_sig.emit(text)

    def error(self, text):
        self.error_sig.emit(text)


    def do_row(self, arg):
        return (self.horizontal_time and arg == 'p') \
            or (not self.horizontal_time and arg == 't')

    def set_time_orientation(self, orientation):
        if orientation not in 'hv':
            self.error('Orientation must be h or v')
            return
        if (orientation == 'h' and self.horizontal_time) or (orientation == 'v' and not self.horizontal_time):
            return
        self.add_undo('flip', None)
        self.grid.flip_orientation()
        self.horizontal_time = not self.horizontal_time
        self.draw_scene()


    # ======== ADD ===========================================================
    def add_plotline(self, name):
        self.insert_plotline(-1, name)

    def add_timeslot(self, name):
        self.insert_timeslot(-1, name)

    # ======== INSERT ========================================================
    def insert_plotline(self, pos, name):
        self._insert(pos, name, 'p')

    def insert_timeslot(self, pos, name):
        self._insert(pos, name, 't')

    def _insert(self, pos, name, arg):
        if self.do_row(arg):
            self.grid.add_row(pos)
            x, y = 0, pos
            self.add_undo('ir', pos)
        else:
            self.grid.add_col(pos)
            x, y = pos, 0
            self.add_undo('ic', pos)
        self.set_cell(x, y, name)
        self.draw_scene()


    # ======== MOVE ==========================================================
    def move_plotline(self, oldpos, newpos):
        self._move(oldpos, newpos, 'p')

    def move_timeslot(self, oldpos, newpos):
        self._move(oldpos, newpos, 't')

    def _move(self, oldpos, newpos, arg):
        foldpos, fnewpos = _fix_movepos(oldpos, newpos)
        if self.do_row(arg):
            self.add_undo('mr', (oldpos, newpos))
            self.grid.move_row(foldpos, fnewpos)
        else:
            self.add_undo('mc', (oldpos, newpos))
            self.grid.move_col(foldpos, fnewpos)
        self.draw_scene()

    # ======== REMOVE ========================================================
    def remove_plotline(self, pos):
        self._remove(pos, 'p')

    def remove_timeslot(self, pos):
        self._remove(pos, 't')

    def _remove(self, pos, arg):
        if self.do_row(arg):
            self.add_undo('rr', (pos, self.grid.row_items(pos)))
            self.grid.remove_row(pos)
        else:
            self.add_undo('rc', (pos, self.grid.col_items(pos)))
            self.grid.remove_col(pos)
        self.draw_scene()

    # ======== CELLS =========================================================
    def edit_cell(self, x, y, text):
        if not text:
            self.prompt('e{} {} {}'.format(x, y, self.grid.item(x,y)[0]))
            return
        self.add_undo('e', (x, y, self.grid.item(x,y)))
        self.set_cell(x, y, text)
        self.draw_scene()

    def clear_cell(self, x, y):
        self.add_undo('e', (x, y, self.grid.item(x,y)))
        self.grid.clear_item(x, y)
        self.draw_scene()

    def set_cell(self, x, y, name):
        if x == 0 and y == 0:
            self.error('Can\'t edit cell 0,0!')
            return
        if x == 0 or y == 0:
            fd = 'bold'
        else:
            fd = 'def'
        size = self.font_data[fd][1].boundingRect(0,0,150,10000,Qt.TextWordWrap,name).size()
        self.grid.set_item(x, y, name, (size.width(), size.height()))

    # ======== UNDO ==========================================================
    def add_undo(self, cmd, arg):
        self.modified_flag = True
        self.undo_stack.append((cmd, arg))

    def undo(self):
        if not self.undo_stack:
            self.error('Nothing to undo')
            return
        cmd, arg = self.undo_stack.pop()
        if cmd == 'e':
            x, y, item = arg
            self.grid.set_item(x, y, *item)
        elif cmd[0] == 'm':
            old, new = _fix_movepos(*arg)
            if cmd[1] == 'r':
                self.grid.move_row(new, old)
            else:
                self.grid.move_col(new, old)
        elif cmd[0] == 'i':
            if cmd[1] == 'r':
                self.grid.remove_row(arg)
            else:
                self.grid.remove_col(arg)
        elif cmd[0] == 'r':
            pos, arr = arg
            if cmd[1] == 'r':
                self.grid.add_row(pos)
                for n, item in enumerate(arr):
                    self.grid.set_item(n, pos, *item)
            else:
                self.grid.add_col(pos)
                for n, item in enumerate(arr):
                    self.grid.set_item(pos, n, *item)
        elif cmd == 'flip':
            self.grid.flip_orientation()
            self.horizontal_time = not self.horizontal_time
        else:
            self.error('Unknown undo: ' + cmd)
            return
        self.draw_scene()


    # ======= FILE HANDLING =============================================

    def is_modified(self):
        return self.modified_flag

    def dirty_window_and_start_in_new_process(self):
        return False #TODO

    def post_new(self):
        self.undo_stack = []
        self.modified_flag = False
        self.grid.clear()
        self.draw_scene()
        self.file_path = ''

    def open_file(self, filename):
        text_matrix = []
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.reader(f, dialect='unix', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                text_matrix.append(row)

        if text_matrix[0][0] in ('HORIZONTAL TIME', 'VERTICAL TIME'):
            if text_matrix[0][0] == ['HORIZONTAL TIME']:
                self.horizontal_time = True
            elif text_matrix[0][0] == ['VERTICAL TIME']:
                self.horizontal_time = False
            text_matrix[0][0] = ''

        self.grid.clear()
        for _ in range(len(text_matrix)-1):
            self.grid.add_row()
        for _ in range(len(text_matrix[0])-1):
            self.grid.add_col()
        for rown, row in enumerate(text_matrix):
            for coln, text in enumerate(row):
                if coln == 0 and rown == 0:
                    continue
                self.set_cell(coln, rown, text)
        self.draw_scene()

        self.file_path = filename
        self.undo_stack = []
        self.modified_flag = False
        return True

    def write_file(self, filename):
        direction = 'HORIZONTAL TIME' if self.horizontal_time else 'VERTICAL TIME'
        first_row = [direction] + self.grid.row_items(0)[1:]
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, dialect='unix', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(first_row)
            for row in list(range(self.grid.count_rows()))[1:]:
                writer.writerow([x[0] for x in self.grid.row_items(row)])

    def post_save(self, saved_filename):
        self.modified_flag = False
        self.file_path = saved_filename


def _fix_movepos(oldpos, newpos):
    if newpos == '+':
        newpos = oldpos + 1
    elif newpos == '-':
        newpos = max(oldpos-1, 1)
    elif oldpos < int(newpos):
        newpos = max(int(newpos) - 1, 1)
    return oldpos, int(newpos)
