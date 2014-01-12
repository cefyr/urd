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
        self.add_plotline('p2')
        self.add_timeslot('t2')
        self.add_timeslot('t3')
        # self.set_item(0,2, 'HAHAHAHAHAHA')
        # self.add_event(1,1,'coooooo')
        # print(self.grid)
        self.add_timeslot('later')
        # self.add_event(0,1,'bam bam')
        self.add_plotline('Jensen')
        self.add_timeslot('the\nend')
        self.set_item(1,1,'winner')
        self.add_plotline('ELPha')
        self.insert_timeslot(1,'prolog')
        self.set_item(3,2,'wuh?\nnnnnn\nHAO')
        self.remove_plotline(3)
        # self.move_timeslot(2,'-')
        # self.move_plotline(1,4)
        self.set_item(2,3, 'det var en gång\ntvå små skurkar')
        # self.remove_timeslot(4)
        # self.remove_timeslot(2)

    def add_plotline_line(self, row):
        y = sum(self.row_heights[:row]) + self.row_heights[row]/2 - self.rowpadding/2
        pen = QPen(QBrush(QColor('#444')), 5, cap=Qt.RoundCap)
        line = self.addLine(self.column_widths[0],y,sum(self.column_widths),y, pen)
        line.setZValue(-10)
        self.plotline_lines.insert(row, line)

    def update_plotline_lines(self):
        for n, line in enumerate(self.plotline_lines):
            if line is None: continue
            y = sum(self.row_heights[:n]) + self.row_heights[n]/2 - self.rowpadding/2
            line.setLine(self.column_widths[0],y,sum(self.column_widths),y)


    def add_plotline(self, name):
        self.grid.add_row()
        self.row_heights.append(0)
        self.set_item(len(self.row_heights)-1, 0, name, header=True)
        self.add_plotline_line(len(self.row_heights)-1)

    def add_timeslot(self, name):
        self.grid.add_column()
        self.column_widths.append(0)
        self.set_item(0, len(self.column_widths)-1, name, header=True)

    def insert_plotline(self, row, name):
        assert row > 0
        self.grid.add_row(row)
        self.row_heights.insert(row, 0)
        self.set_item(row, 0, name, header=True)

    def insert_timeslot(self, column, name):
        assert column > 0
        self.grid.add_column(column)
        self.column_widths.insert(column, 0)
        self.set_item(0, column, name, header=True)

    def remove_plotline(self, row):
        assert row > 0
        for item in self.grid.row_items(row):
            item.remove()
        self.grid.remove_row(row)
        del self.row_heights[row]
        self.removeItem(self.plotline_lines[row])
        del self.plotline_lines[row]
        self.update_cell_pos()
        self.update_lines()
        self.update_plotline_lines()

    def remove_timeslot(self, column):
        assert column > 0
        for item in self.grid.column_items(column):
            item.remove()
        self.grid.remove_column(column)
        del self.column_widths[column]
        self.update_cell_pos()
        self.update_lines()
        self.update_plotline_lines()

    def fix_movepos(self, oldpos, newpos):
        if newpos == '+':
            newpos = oldpos + 2
        elif newpos == '-':
            newpos = max(oldpos-1, 1)
        elif oldpos < newpos:
            newpos -= 1
        return oldpos, newpos

    def move_plotline(self, oldpos, newpos):
        oldpos, newpos = self.fix_movepos(oldpos, newpos)
        self.grid.move_row(oldpos, newpos)
        row = self.row_heights.pop(oldpos)
        self.row_heights.insert(newpos, row)
        self.update_cell_pos()
        self.update_plotline_lines()

    def move_timeslot(self, oldpos, newpos):
        oldpos, newpos = self.fix_movepos(oldpos, newpos)
        self.grid.move_column(oldpos, newpos)
        column = self.column_widths.pop(oldpos)
        self.column_widths.insert(newpos, column)
        self.update_cell_pos()

    def set_item(self, row, column, text, header=False):
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
