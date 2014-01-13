#!/usr/bin/env python3

from PyQt4 import QtGui
from PyQt4.QtGui import QBrush, QColor, QPen
from PyQt4.QtCore import pyqtSignal, Qt

from matrix import Matrix


class Scene(QtGui.QGraphicsScene):
    print_ = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.horizontal_time = False

        self.setBackgroundBrush(QColor('#222'))
        self.row_heights = [0]
        self.column_widths = [0]
        self.colpadding = 16
        self.rowpadding = 8

        self.brush = QBrush(QColor('#222'))

        font = QtGui.QFont('Serif', 10)
        self.fm = QtGui.QFontMetricsF(font)

        self.header_font = QtGui.QFont('Serif', 10)
        self.header_font.setBold(True)
        self.header_fm = QtGui.QFontMetricsF(self.header_font)


        self.line_pen = QPen(QColor('black'))
        self.hline = self.addLine(0,0,0,0, self.line_pen)
        self.vline = self.addLine(0,0,0,0, self.line_pen)

        self.plotline_lines = [None]

        self.grid = Matrix(self, font, self.brush)

        # Debug
        self.add_plotline('p1')
        self.add_timeslot('t1123456')
        # self.add_plotline('p2')
        self.add_timeslot('t2')
        self.add_timeslot('t3')
        # # self.set_item(0,2, 'HAHAHAHAHAHA')
        # # self.add_event(1,1,'coooooo')
        # # print(self.grid)
        self.add_timeslot('later')
        # # self.add_event(0,1,'bam bam')
        # self.add_plotline('Jensen')
        self.add_timeslot('the\nend')
        # self.set_item(1,1,'winner')
        # self.add_plotline('ELPha')
        # self.insert_timeslot(1,'prolog')
        # self.set_item(2,3,'wuh?\nnnnnn\nHAO')
        # self.remove_plotline(3)
        self.move_timeslot(5,1)
        self.move_timeslot(5,1)
        # # self.move_plotline(1,4)
        # self.set_item(2,3, 'det var en gång\ntvå små skurkar')
        # self.remove_timeslot(4)
        # self.remove_timeslot(2)

    def set_plotline_line_pos(self, line, pos):
        if self.horizontal_time:
            y = sum(self.row_heights[:pos]) + self.row_heights[pos]/2 - self.rowpadding/2
            line.setLine(self.column_widths[0], y, sum(self.column_widths), y)
        else:
            x = sum(self.column_widths[:pos]) + self.column_widths[pos]/2 - self.colpadding/2
            line.setLine(x, self.row_heights[0], x, sum(self.row_heights))

    def add_plotline_line(self, pos):
        pen = QPen(QBrush(QColor('#444')), 5, cap=Qt.RoundCap)
        line = self.addLine(0,0,0,0,pen)
        self.set_plotline_line_pos(line, pos)
        line.setZValue(-10)
        self.plotline_lines.insert(pos, line)

    def update_plotline_lines(self):
        for n, line in enumerate(self.plotline_lines):
            if line is None: continue
            self.set_plotline_line_pos(line, n)

    # ==== ADD =======================================================
    def add_plotline(self, name):
        if self.horizontal_time:
            self.insert_row(1, name, append=True)
            self.add_plotline_line(len(self.row_heights)-1)
        else:
            self.insert_column(1, name, append=True)
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
        self.add_plotline_line(pos)

    def insert_timeslot(self, pos, name):
        if self.horizontal_time:
            self.insert_column(pos, name)
        else:
            self.insert_row(pos, name)

    def insert_row(self, row, name, append=False):
        row = max(1, min(row, len(self.row_heights)))
        if append:
            row = len(self.row_heights)
        self.grid.add_row(row)
        self.row_heights.insert(row, 0)
        self.set_item(row, 0, name, header=True)

    def insert_column(self, column, name, append=False):
        column = max(1, min(column, len(self.column_widths)))
        if append:
            column = len(self.column_widths)
        self.grid.add_column(column)
        self.column_widths.insert(column, 0)
        self.set_item(0, column, name, header=True)

    # ==== REMOVE ====================================================
    def remove_plotline(self, pos):
        if pos in range(len(self.plotline_lines)):
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
            self.error.emit('Row doesn\'t exist')
            return
        for item in self.grid.row_items(row):
            item.remove()
        self.grid.remove_row(row)
        del self.row_heights[row]
        self.update_cell_pos()
        self.update_lines()
        self.update_plotline_lines()

    def remove_column(self, column):
        if not column in range(self.grid.count_columns()):
            self.error.emit('Column doesn\'t exist')
            return
        for item in self.grid.column_items(column):
            item.remove()
        self.grid.remove_column(column)
        del self.column_widths[column]
        self.update_cell_pos()
        self.update_lines()
        self.update_plotline_lines()

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

    def fix_movepos(self, oldpos, newpos):
        if newpos == '+':
            newpos = oldpos + 1
        elif newpos == '-':
            newpos = max(oldpos-1, 1)
        elif oldpos < int(newpos):
            newpos = max(int(newpos) - 1, 1)
        return oldpos, int(newpos)

    def move_row(self, oldpos, newpos):
        if not oldpos in range(1, self.grid.count_rows()):
            self.error.emit('Row doesn\'t exist')
            return
        oldpos, newpos = self.fix_movepos(oldpos, newpos)
        self.grid.move_row(oldpos, newpos)
        row = self.row_heights.pop(oldpos)
        self.row_heights.insert(newpos, row)
        self.update_cell_pos()

    def move_column(self, oldpos, newpos):
        if not oldpos in range(1, self.grid.count_columns()):
            self.error.emit('Column doesn\'t exist')
            return
        oldpos, newpos = self.fix_movepos(oldpos, newpos)
        self.grid.move_column(oldpos, newpos)
        column = self.column_widths.pop(oldpos)
        self.column_widths.insert(newpos, column)
        self.update_cell_pos()



    def set_item(self, row, column, text, header=False):
        text = text.replace('\\n', '\n')
        if header:
            size = self.header_fm.size(0, text)
        else:
            size = self.fm.size(0, text)
        x = sum(self.column_widths[:column])
        y = sum(self.row_heights[:row])
        if header:
            font = self.header_font
        else:
            font = None
        self.grid.set_item(row, column, text, font, size, x, y)

        self.update_cell_size(row, column)
        self.update_cell_pos()
        self.update_plotline_lines()

    def update_cell_size(self, row, column):
        self.row_heights[row] = max(x.height() for x in self.grid.row_items(row)) + self.rowpadding
        self.column_widths[column] = max(x.width() for x in self.grid.column_items(column)) + self.colpadding
        self.update_lines()

    def update_lines(self):
        hy = self.row_heights[0] - self.rowpadding/2
        vx = self.column_widths[0] - self.colpadding/2
        self.hline.setLine(0,hy,sum(self.column_widths),hy)
        self.vline.setLine(vx,0,vx,sum(self.row_heights))

    def update_cell_pos(self):
        for r in range(self.grid.count_rows()):
            for c in range(self.grid.count_columns()):
                item = self.grid.item(r,c)
                x = sum(self.column_widths[:c]) + self.column_widths[c]/2 - self.colpadding/2
                y = sum(self.row_heights[:r]) + self.row_heights[r]/2 - self.rowpadding/2
                item.set_pos(x,y)


if __name__ == '__main__':
    s = Scene()
