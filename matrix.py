
from PyQt4 import QtGui, QtCore

from eventitem import EventItem


class Matrix():
    def __init__(self, scene, item_font, item_brush):
        self.scene = scene
        self.item_font = item_font
        self.item_brush = item_brush
        self.data = [[self._default_item()]]

    def __str__(self):
        return '\n'.join('\t|\t'.join(x.text() for x in row) for row in self.data)

    def size(self):
        return ('rows', len(self.data), 'cols', len(self.data[0]))

    def _default_item(self):
        item = EventItem(self.scene, self.item_font, self.item_brush)
        # item = QtGui.QGraphicsSimpleTextItem(scene=self.scene)
        # item.setFont(self.item_font)
        # item.setBrush(self.item_brush)
        # item.hide()
        return item #(item, QtCore.QSizeF(0,0))

    def count_rows(self):
        return len(self.data)

    def count_columns(self):
        return len(self.data[0])

    def add_row(self, pos=-1):
        data = [self._default_item() for _ in range(len(self.data[0]))]
        if pos == -1:
            self.data.append(data)
        else:
            self.data.insert(pos, data)

    def add_column(self, pos=-1):
        for n in range(len(self.data)):
            if pos == -1:
                self.data[n].append(self._default_item())
            else:
                self.data[n].insert(pos, self._default_item())

    def remove_row(self, pos):
        del self.data[pos]

    def remove_column(self, pos):
        for n in range(len(self.data)):
            del self.data[n][pos]

    def move_row(self, oldpos, newpos):
        row = self.data.pop(oldpos)
        self.data.insert(newpos, row)

    def move_column(self, oldpos, newpos):
        for n in range(len(self.data)):
            x = self.data[n].pop(oldpos)
            self.data[n].insert(newpos, x)

    def row_items(self, pos):
        return self.data[pos]

    def column_items(self, pos):
        return [x[pos] for x in self.data]

    def item(self, row, column):
        return self.data[row][column]

    def set_item(self, row, column, text, font, size, x, y):
        item = self.data[row][column]
        item.set_text(text)
        if font:
            item.set_font(font)
        item.set_pos(x,y)
        item.set_size(size)
        item.show()

    def clear_item(self, row, column):
        self.data[row][column].hide()
