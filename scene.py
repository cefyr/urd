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
        self.move_timeslot(2,'-')
        self.move_plotline(1,4)
        # self.remove_timeslot(4)
        # self.remove_timeslot(2)


    def add_plotline(self, name):
        self.grid.add_row()
        self.row_heights.append(0)
        self.set_item(len(self.row_heights)-1, 0, name)

    def add_timeslot(self, name):
        self.grid.add_column()
        self.column_widths.append(0)
        self.set_item(0, len(self.column_widths)-1, name)

    def insert_plotline(self, row, name):
        assert row > 0
        self.grid.add_row(row)
        self.row_heights.insert(row, 0)
        self.set_item(row, 0, name)

    def insert_timeslot(self, column, name):
        assert column > 0
        self.grid.add_column(column)
        self.column_widths.insert(column, 0)
        self.set_item(0, column, name)

    def remove_plotline(self, row):
        assert row > 0
        for item in self.grid.row_items(row):
            self.removeItem(item)
        self.grid.remove_row(row)
        del self.row_heights[row]
        self.update_cell_pos()

    def remove_timeslot(self, column):
        assert column > 0
        for item in self.grid.column_items(column):
            self.removeItem(item)
        self.grid.remove_column(column)
        del self.column_widths[column]
        self.update_cell_pos()

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

    def move_timeslot(self, oldpos, newpos):
        oldpos, newpos = self.fix_movepos(oldpos, newpos)
        self.grid.move_column(oldpos, newpos)
        column = self.column_widths.pop(oldpos)
        self.column_widths.insert(newpos, column)
        self.update_cell_pos()


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
