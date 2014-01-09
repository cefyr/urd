#!/usr/bin/env python3

from PyQt4 import QtGui

from matrix import Matrix


class Scene(QtGui.QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setBackgroundBrush(QtGui.QColor('#222'))
        self.row_heights = [0]
        self.column_widths = [0]
        self.hpadding = 16
        self.vpadding = 8

        self.brush = QtGui.QBrush(QtGui.QColor('#ddd'))

        font = QtGui.QFont('Serif')
        self.fm = QtGui.QFontMetricsF(font)

        self.header_font = QtGui.QFont(font)
        self.header_font.setBold(True)
        self.header_fm = QtGui.QFontMetricsF(self.header_font)


        self.grid = Matrix(self, font, self.brush)

        # Debug
        self.add_plotline('p1')
        self.add_timeslot('t1')
        self.add_plotline('p2')
        self.add_timeslot('t2')
        self.add_timeslot('t3')
        self.add_event(0,0,'coooooo')
        # print(self.grid)
        self.add_timeslot('later')
        self.add_event(0,1,'bam bam')
        self.add_plotline('Jensen')
        self.add_timeslot('the\nend')
        self.add_event(1,1,'winner')
        self.add_plotline('ELPha')
        # self.insert_timeslot(1,'prolog')
        self.add_event(1,0,'wuh?')
        # self.grid.dump()
        # self.draw()

    def add_plotline(self, name):
        self.insert_plotline(0, name, append=True)
        # item = self.addSimpleText(name, self.header_font)
        # item.setPos(0, sum(self.row_heights))
        # item.setBrush(self.brush)
        # size = self.header_fm.size(0, name)
        # self.row_heights.append(size.height() + self.vpadding)
        # self.grid.add_row([(item,size)])
        # self.update_column_width(0)

    def add_timeslot(self, name):
        self.insert_timeslot(0, name, append=True)
        # item = self.addSimpleText(name, self.header_font)
        # item.setPos(sum(self.column_widths), 0)
        # item.setBrush(self.brush)
        # size = self.header_fm.size(0, name)
        # self.column_widths.append(size.width() + self.hpadding)
        # self.grid.add_column([(item,size)])
        # self.update_row_height(0)

    def insert_plotline(self, pos, name, append=False):
        print(name)
        item = self.addSimpleText(name, self.header_font)
        item.setPos(0, sum(self.row_heights))
        item.setBrush(self.brush)
        size = self.header_fm.size(0, name)
        self.row_heights.append(size.height() + self.vpadding)
        if append:
            self.grid.add_row([(item,size)])
        else:
            self.grid.insert_row(pos+1, [(item,size)])
        self.update_column_width(0)

    def insert_timeslot(self, pos, name, append=False):
        print(name)
        item = self.addSimpleText(name, self.header_font)
        item.setPos(sum(self.column_widths), 0)
        item.setBrush(self.brush)
        size = self.header_fm.size(0, name)
        self.column_widths.append(size.width() + self.hpadding)
        if append:
            self.grid.add_column([(item,size)])
        else:
            self.grid.insert_column(pos+1, [(item,size)])
        self.update_row_height(0)

    def add_event(self, plotline, timeslot, text):
        print(text)
        size = self.fm.size(0, text)
        x = sum(self.column_widths[:timeslot+1])
        y = sum(self.row_heights[:plotline+1])
        self.grid.set_item(plotline+1, timeslot+1, text, size, x, y)

        self.update_row_height(timeslot+1)
        self.update_column_width(plotline+1)

        # item = self.addSimpleText(name, self.header_font)
        # item.setPos(0, sum(self.row_heights))
        # item.setBrush(self.brush)
        # size = self.header_fm.size(0, name)
        # self.row_heights.append(size.height() + self.vpadding)
        # self.grid.insert_row(pos+1, [(item,size)])
        # self.update_column_width(0)


    def update_row_height(self, pos):
        new_height = max(x.height() for x in self.grid.row_sizes(pos)) + self.vpadding
        if new_height != self.row_heights[pos]:
            self.update_row_positions(new_height - self.row_heights[pos], pos+1)
        self.row_heights[pos] = new_height

    def update_column_width(self, pos):
        new_width = max(x.width() for x in self.grid.column_sizes(pos)) + self.hpadding
        print('new w', new_width)
        if new_width != self.column_widths[pos]:
            self.update_column_positions(new_width - self.column_widths[pos], pos+1)
        self.column_widths[pos] = new_width

    def update_row_positions(self, delta, start):
        for n in range(start, self.grid.count_rows()):
            for item in self.grid.row_items(n):
                item.moveBy(0, delta)

    def update_column_positions(self, delta, start):
        print('delta', delta)
        for n in range(start, self.grid.count_columns()):
            for item in self.grid.column_items(n):
                if not item.text():
                    continue
                print(item.text())
                print('befor', item.x())
                item.moveBy(delta, 0)
                print('after', item.x())

    def draw(self):
        pass


if __name__ == '__main__':
    s = Scene()