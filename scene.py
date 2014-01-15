#!/usr/bin/env python3

import csv

from PyQt4 import QtGui
from PyQt4.QtGui import QBrush, QColor, QPen
from PyQt4.QtCore import pyqtSignal, Qt

from libsyntyche.filehandling import FileHandler

from matrix import Matrix


class Scene(QtGui.QGraphicsScene, FileHandler):
    print_ = pyqtSignal(str)
    error_sig = pyqtSignal(str)
    prompt_sig = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.horizontal_time = False

        self.setBackgroundBrush(QColor('#222'))
        self.border = 24
        self.rowpadding = 8
        self.colpadding = 16
        self.row_heights = [0]
        self.column_widths = [0]
        self.row_numbers = [None]
        self.column_numbers = [None]
        self.plotline_lines = [None]

        self.undo_stack = []
        self.undo_plotline_buffer = ()

        self.line_pen = QPen(QColor('black'))
        self.hline = self.addLine(0,0,0,0, self.line_pen)
        self.vline = self.addLine(0,0,0,0, self.line_pen)

        self.brush = QBrush(QColor('#222'))

        font = QtGui.QFont('Serif', 10)
        self.fm = QtGui.QFontMetricsF(font)

        self.header_font = QtGui.QFont('Serif', 10)
        self.header_font.setBold(True)
        self.header_fm = QtGui.QFontMetricsF(self.header_font)

        self.grid = Matrix(self, font, self.brush)

        # Debug
        self.add_plotline('p1')
        self.add_plotline('"BLO"OP"')
        self.add_timeslot('t11\'2\'3456')
        self.add_timeslot('t2')
        self.add_timeslot('ththw\\fat3')
        self.add_timeslot('later')
        self.add_timeslot('the\nend')

        # self.clear_scene()

        # print('grid', self.grid)

        # self.write_file('test.csv')

    # ====== NUKE EVERYTHING =========================================

    def clear_scene(self):
        self.row_heights, self.column_widths = [0], [0]

        for item in self.row_numbers[1:] + self.column_numbers[1:] + self.plotline_lines[1:]:
            self.removeItem(item)
        self.row_numbers = [None]
        self.column_numbers = [None]
        self.plotline_lines = [None]

        self.hline.setLine(0,0,0,0)
        self.vline.setLine(0,0,0,0)

        for row in list(range(self.grid.count_rows()))[:0:-1]:
            for item in self.grid.row_items(row):
                item.remove()
            self.grid.remove_row(row)

        for n,item in list(enumerate(self.grid.row_items(0)))[:0:-1]:
            print('n',n)
            item.remove()
            self.grid.remove_column(n)


    # ====== UNDO ====================================================

    def add_undo(self, cmd, arg):
        # Move
        if cmd[0] == 'm':
            old, new = arg
            if old < new:
                new += 1
            self.undo_stack.append((cmd, (old, new)))
        # Add
        elif cmd[0] == 'a':
            pos, arr = arg
            items = [x.text() if x.is_visible() else None for x in arr]
            self.undo_stack.append((cmd, (pos, items, self.undo_plotline_buffer)))
            self.undo_plotline_buffer = ()
        # Remove
        elif cmd[0] == 'r':
            pos, arr = arg
            items = [x.text() if x.is_visible() else None for x in arr]
            self.undo_stack.append((cmd, (pos, items, self.undo_plotline_buffer)))
            self.undo_plotline_buffer = ()
        else:
            self.undo_stack.append((cmd, arg))

    def undo(self, _):
        if not self.undo_stack:
            return
        undoitem = self.undo_stack.pop()
        cmd, arg = undoitem
        # Move
        if cmd[0] == 'm':
            if cmd[1] == 'r':
                self.move_row(*arg)
            elif cmd[1] == 'c':
                self.move_column(*arg)
        # Clear
        elif cmd[0] == 'c':
            self.clear_cell(*arg, add_undo=False)
        # Edit
        elif cmd[0] == 'e':
            self.set_cell(*arg)
        # Add
        elif cmd[0] == 'a':
            pos, items = arg
            if cmd[1] == 'r':
                self.insert_row(pos, items[0], add_undo=False)
                for n, item in list(enumerate(items))[1:]:
                    if item is not None:
                        self.set_cell(pos, n, item)
            elif cmd[1] == 'c':
                self.insert_column(pos, items[0], add_undo=False)
                for n, item in list(enumerate(items))[1:]:
                    if item is not None:
                        self.set_cell(n, pos, item)


    # ====== CONVENIENCE FUNCTIONS ===================================

    def _coord(self, arr, padding, pos):
        return self.border + sum(arr[:pos]) + arr[pos]/2 - padding/2

    def row_y(self, row):
        return self._coord(self.row_heights, self.rowpadding, row)

    def col_x(self, col):
        return self._coord(self.column_widths, self.colpadding, col)

    def prompt(self, text):
        self.prompt_sig.emit(text)

    def error(self, text):
        self.error_sig.emit(text)


    # ==== ADD =======================================================

    def add_plotline(self, name):
        if self.horizontal_time:
            self.insert_row(1, name, append=True)
            self.undo_plotline_buffer = ('r', len(self.row_heights)-1)
            self.add_plotline_line(len(self.row_heights)-1)
        else:
            self.insert_column(1, name, append=True)
            self.undo_plotline_buffer = ('r', len(self.column_widths)-1)
            self.add_plotline_line(len(self.column_widths)-1)

    def add_timeslot(self, name):
        if self.horizontal_time:
            self.insert_column(1, name, append=True)
        else:
            self.insert_row(1, name, append=True)


    # ==== INSERT ====================================================

    def insert_plotline(self, pos, name):
        if self.horizontal_time:
            self.insert_row(pos, name)
        else:
            self.insert_column(pos, name)
        self.undo_plotline_buffer = ('r', pos)
        self.add_plotline_line(pos)

    def insert_timeslot(self, pos, name):
        if self.horizontal_time:
            self.insert_column(pos, name)
        else:
            self.insert_row(pos, name)

    def insert_row(self, row, name, append=False, add_undo=True):
        row = max(1, min(row, len(self.row_heights)))
        if append:
            row = len(self.row_heights)
        self.grid.add_row(row)
        self.row_heights.insert(row, 0)
        self.set_cell(row, 0, name, header=True)
        self.add_row_number()

    def insert_column(self, column, name, append=False, add_undo=True):
        column = max(1, min(column, len(self.column_widths)))
        if append:
            column = len(self.column_widths)
        self.grid.add_column(column)
        self.column_widths.insert(column, 0)
        self.set_cell(0, column, name, header=True)
        self.add_column_number()


    # ==== REMOVE ====================================================

    def remove_plotline(self, pos):
        if pos in range(len(self.plotline_lines)):
            self.undo_plotline_buffer = ('a', pos)
            self.removeItem(self.plotline_lines[pos])
            del self.plotline_lines[pos]
        if self.horizontal_time:
            self.remove_row(pos)
        else:
            self.remove_column(pos)

    def remove_timeslot(self, pos):
        if self.horizontal_time:
            self.remove_column(pos)
        else:
            self.remove_row(pos)

    def remove_row(self, row):
        if not row in range(self.grid.count_rows()):
            self.error('Row doesn\'t exist')
            return
        self.add_undo('ar', (row, self.grid.row_items(row)))
        for item in self.grid.row_items(row):
            item.remove()
        self.grid.remove_row(row)
        del self.row_heights[row]
        self.update_cell_pos()
        self.update_lines()
        self.update_plotline_lines()
        self.remove_row_number()

    def remove_column(self, column):
        if not column in range(self.grid.count_columns()):
            self.error('Column doesn\'t exist')
            return
        self.add_undo('ac', (column, self.grid.column_items(column)))
        for item in self.grid.column_items(column):
            item.remove()
        self.grid.remove_column(column)
        del self.column_widths[column]
        self.update_cell_pos()
        self.update_lines()
        self.update_plotline_lines()
        self.remove_column_number()


    # ==== MOVE ======================================================

    def move_plotline(self, oldpos, newpos):
        if self.horizontal_time:
            self.move_row(oldpos, newpos)
        else:
            self.move_column(oldpos, newpos)
        self.update_plotline_lines()

    def move_timeslot(self, oldpos, newpos):
        if self.horizontal_time:
            self.move_column(oldpos, newpos)
        else:
            self.move_row(oldpos, newpos)

    def _fix_movepos(self, oldpos, newpos):
        if newpos == '+':
            newpos = oldpos + 1
        elif newpos == '-':
            newpos = max(oldpos-1, 1)
        elif oldpos < int(newpos):
            newpos = max(int(newpos) - 1, 1)
        return oldpos, int(newpos)

    def move_row(self, oldpos, newpos):
        if not oldpos in range(1, self.grid.count_rows()):
            self.error('Row doesn\'t exist')
            return
        oldpos, newpos = self._fix_movepos(oldpos, newpos)
        self.grid.move_row(oldpos, newpos)
        row = self.row_heights.pop(oldpos)
        self.row_heights.insert(newpos, row)
        self.update_cell_pos()
        self.update_numbers()
        self.add_undo('mr', (newpos, oldpos))

    def move_column(self, oldpos, newpos):
        if not oldpos in range(1, self.grid.count_columns()):
            self.error('Column doesn\'t exist')
            return
        oldpos, newpos = self._fix_movepos(oldpos, newpos)
        self.grid.move_column(oldpos, newpos)
        column = self.column_widths.pop(oldpos)
        self.column_widths.insert(newpos, column)
        self.update_cell_pos()
        self.update_numbers()
        self.add_undo('mc', (newpos, oldpos))


    # ======= CELL HANDLING =============================================

    def edit_cell(self, column, row, text): # yes, that's the correct order
        if column not in range(self.grid.count_columns()):
            self.error('Column doesn\'t exist')
        elif row not in range(self.grid.count_rows()):
            self.error('Row doesn\'t exist')
        elif not text:
            oldtext = self.grid.item(row, column).text()
            self.prompt('e{} {} {}'.format(column, row, oldtext))
        else:
            item = self.grid.item(row, column)
            if not item.is_visible():
                self.add_undo('c', (column, row))
            else:
                self.add_undo('e', (row, column, self.grid.item(row, column).text()))
            self.set_cell(row, column, text)

    def clear_cell(self, column, row, add_undo=True):
        if column not in range(self.grid.count_columns()):
            self.error('Column doesn\'t exist')
        elif row not in range(self.grid.count_rows()):
            self.error('Row doesn\'t exist')
        else:
            if add_undo:
                self.add_undo('e', (row, column, self.grid.item(row, column).text()))
            self.grid.clear_item(row, column)
            self.update_cell_size(row, column)
            self.update_cell_pos()
            self.update_plotline_lines()
            self.update_numbers()

    def set_cell(self, row, column, text, header=False):
        text = text.replace('\\n', '\n')
        if header:
            size = self.header_fm.size(0, text)
        else:
            size = self.fm.size(0, text)
        x = self.border + sum(self.column_widths[:column])
        y = self.border + sum(self.row_heights[:row])
        if header:
            font = self.header_font
        else:
            font = None
        self.grid.set_item(row, column, text, font, size, x, y)

        self.update_cell_size(row, column)
        self.update_cell_pos()
        self.update_plotline_lines()
        self.update_numbers()


    def update_cell_size(self, row, column):
        self.row_heights[row] = max(x.height() for x in self.grid.row_items(row)) + self.rowpadding
        self.column_widths[column] = max(x.width() for x in self.grid.column_items(column)) + self.colpadding
        self.update_lines()

    def update_cell_pos(self):
        for r in range(self.grid.count_rows()):
            for c in range(self.grid.count_columns()):
                item = self.grid.item(r,c)
                item.set_pos(self.col_x(c), self.row_y(r))


    # ======= LINES =====================================================

    def update_lines(self):
        hy = self.border + self.row_heights[0] - self.rowpadding/2
        vx = self.border + self.column_widths[0] - self.colpadding/2
        self.hline.setLine(0,hy,self.border + sum(self.column_widths),hy)
        self.vline.setLine(vx,0,vx,self.border + sum(self.row_heights))


    # ======= PLOTLINE LINES ============================================

    def _set_plotline_line_pos(self, line, pos):
        if self.horizontal_time:
            y = self.row_y(pos)
            line.setLine(self.border+self.column_widths[0], y, self.border+sum(self.column_widths), y)
        else:
            x = self.col_x(pos)
            line.setLine(x, self.border+self.row_heights[0], x, self.border+sum(self.row_heights))

    def add_plotline_line(self, pos):
        pen = QPen(QBrush(QColor('#444')), 5, cap=Qt.RoundCap)
        line = self.addLine(0,0,0,0,pen)
        self._set_plotline_line_pos(line, pos)
        line.setZValue(-10)
        self.plotline_lines.insert(pos, line)

    def update_plotline_lines(self):
        for n, line in enumerate(self.plotline_lines):
            if line is None: continue
            self._set_plotline_line_pos(line, n)


    # ======= NUMBERS ===================================================

    def add_row_number(self):
        self._add_number(self.row_numbers)

    def add_column_number(self):
        self._add_number(self.column_numbers)

    def _add_number(self, arr):
        num = self.addSimpleText(str(len(arr)))
        arr.append(num)
        self.update_numbers()

    def remove_row_number(self):
        self._remove_number(self.row_numbers)

    def remove_column_number(self):
        self._remove_number(self.column_numbers)

    def _remove_number(self, arr):
        self.removeItem(arr[-1])
        del arr[-1]
        self.update_numbers()

    def update_numbers(self):
        for n, item in enumerate(self.row_numbers):
            if not n: continue
            item.setPos(4, self.row_y(n)-item.boundingRect().height()/2)
        for n, item in enumerate(self.column_numbers):
            if not n: continue
            item.setPos(self.col_x(n)-item.boundingRect().width()/2, 4)


    # ======= FILE HANDLING =============================================

    def is_modified(self):
        return False #TODO

    def dirty_window_and_start_in_new_process(self):
        return False #TODO

    def post_new(self):
        self.clear_scene()

    def open_file(self, filename):
        text_matrix = []
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.reader(f, dialect='unix', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                text_matrix.append(row)


        return True

    def write_file(self, filename):
        direction = 'HORIZONTAL TIME' if self.horizontal_time else 'VERTICAL TIME'
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, dialect='unix', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([direction])
            for row in range(self.grid.count_rows()):
                writer.writerow([x.text() for x in self.grid.row_items(row)])

    def post_save(self, saved_filename):
        pass


if __name__ == '__main__':
    s = Scene()
