
def default_item():
    return ('', (0,0))

class Matrix():
    def __init__(self):
        self.data = [[default_item()]]

    def __str__(self):
        return '\n'.join(repr(row) for row in self.data)
        # return '\n'.join('\t|\t'.join(repr(x) for x in row) for row in self.data)

    def clear(self):
        self.data = [[default_item()]]

    def flip_orientation(self):
        self.data = list(map(list, zip(*self.data)))

    def count_rows(self):
        return len(self.data)

    def count_cols(self):
        return len(self.data[0])

    def add_row(self, pos=-1):
        data = [default_item() for _ in range(len(self.data[0]))]
        if pos == -1:
            self.data.append(data)
        else:
            self.data.insert(pos, data)

    def add_col(self, pos=-1):
        for n in range(len(self.data)):
            if pos == -1:
                self.data[n].append(default_item())
            else:
                self.data[n].insert(pos, default_item())

    def remove_row(self, pos):
        del self.data[pos]

    def remove_col(self, pos):
        for n in range(len(self.data)):
            del self.data[n][pos]

    def move_row(self, oldpos, newpos):
        row = self.data.pop(oldpos)
        self.data.insert(newpos, row)

    def move_col(self, oldpos, newpos):
        for n in range(len(self.data)):
            x = self.data[n].pop(oldpos)
            self.data[n].insert(newpos, x)

    def row_items(self, pos):
        return self.data[pos]

    def col_items(self, pos):
        return [x[pos] for x in self.data]

    def item(self, col, row):
        return self.data[row][col]

    def set_item(self, col, row, text, size):
        self.data[row][col] = (text, size)

    def clear_item(self, col, row):
        self.data[row][col] = default_item()
