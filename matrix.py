
from PyQt4 import QtGui, QtCore




class Matrix():
    def __init__(self, scene, item_font, item_brush):
        self.scene = scene
        self.item_font = item_font
        self.item_brush = item_brush
        self.data = [[self.default_item()]]

    def __str__(self):
        return '\n'.join('\t|\t'.join(x[0].text() for x in row) for row in self.data)

    def default_item(self):
        item = QtGui.QGraphicsSimpleTextItem(scene=self.scene)
        item.setFont(self.item_font)
        item.setBrush(self.item_brush)
        return (item, QtCore.QSizeF(0,0))

    def pad_row(self, data):
        data.extend([self.default_item()]*(len(self.data[0])-len(data)))

    def pad_column(self, data):
        data.extend([self.default_item()]*(len(self.data)-len(data)))

    def count_rows(self):
        return len(self.data)

    def count_columns(self):
        return len(self.data[0])

    def add_row(self, data):
        self.pad_row(data)
        self.data.append(data)

    def add_column(self, data):
        self.pad_column(data)
        for n in range(len(self.data)):
            self.data[n].append(data[n])

    def insert_row(self, pos, data):
        self.pad_row(data)
        self.data.insert(pos, data)

    def insert_column(self, pos, data):
        self.pad_column(data)
        for n in range(len(self.data)):
            self.data[n].insert(pos, data[n])

    def remove_row(self, pos):
        del self.data[pos]

    def remove_column(self, pos):
        for n in range(len(self.data)):
            del self.data[n][pos]

    def row_items(self, pos):
        return [x[0] for x in self.data[pos]]

    def column_items(self, pos):
        return [x[pos][0] for x in self.data]

    def row_sizes(self, pos):
        return [x[1] for x in self.data[pos]]

    def column_sizes(self, pos):
        return [x[pos][1] for x in self.data]

    def item(self, row, column):
        return self.data[row][column][0]

    def item_size(self, row, column):
        return self.data[row][column][1]

    def set_item(self, row, column, text, size, x, y):
        item = self.data[row][column]
        item[0].setText(text)
        item[0].setPos(x,y)
        item[1].scale(size, QtCore.Qt.IgnoreAspectRatio)