#!/usr/bin/env python3

from PyQt4 import QtGui

from matrix import Matrix


class Scene(QtGui.QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setBackgroundBrush(QtGui.QColor('#222'))
        self.row_heights = [0]
        self.column_widths = [0]
        self.colpadding = 16
        self.rowpadding = 8

        self.brush = QtGui.QBrush(QtGui.QColor('#ddd'))

        font = QtGui.QFont('Serif')
        self.fm = QtGui.QFontMetricsF(font)

        self.header_font = QtGui.QFont(font)
        self.header_font.setBold(True)
        self.header_fm = QtGui.QFontMetricsF(self.header_font)


        self.grid = Matrix(self, font, self.brush)

        # Debug
        self.add_plotline('p1')
        self.add_timeslot('t1123456')
        self.add_plotline('p2')
        self.add_timeslot('t2')
        self.add_timeslot('t3')
        self.set_item(0,2, 'HAHAHAHAHAHA')
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


    def add_plotline(self, name):
        self.grid.add_row()
        self.row_heights.append(0)
        self.set_item(len(self.row_heights)-1, 0, name)

    def add_timeslot(self, name):
        self.grid.add_column()
        self.column_widths.append(0)
        self.set_item(0, len(self.column_widths)-1, name)

    def insert_plotline(self, pos, name):
        if pos < 1:
            pos = 1
        self.grid.add_row(pos)
        self.row_heights.insert(pos, 0)
        self.set_item(pos, 0, name)

    def insert_timeslot(self, pos, name):
        if pos < 1:
            pos = 1
        self.grid.add_column(pos)
        self.column_widths.insert(pos, 0)
        self.set_item(0, pos, name)

    def set_item(self, row, column, text):
        size = self.fm.size(0, text)
        x = sum(self.column_widths[:column])
        y = sum(self.row_heights[:row])
        self.grid.set_item(row, column, text, size, x, y)

        self.update_cell_size(row, column)
        self.update_cell_pos()

    def update_cell_size(self, row, column):
        self.row_heights[row] = max(x.height() for x in self.grid.row_sizes(row)) + self.rowpadding
        self.column_widths[column] = max(x.width() for x in self.grid.column_sizes(column)) + self.colpadding


    def update_cell_pos(self):
        for r in range(self.grid.count_rows()):
            for c in range(self.grid.count_columns()):
                item = self.grid.item(r,c)
                item.setPos(sum(self.column_widths[:c]), sum(self.row_heights[:r]))


if __name__ == '__main__':
    s = Scene()
