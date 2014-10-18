
def default_item():
    return ('', (0,0))

class Matrix():
    def __init__(self):
        self.data = [[default_item()]]

    def __str__(self):
        return '\n'.join(repr(row) for row in self.data)
        # return '\n'.join('\t|\t'.join(repr(x) for x in row) for row in self.data)

    def __contains__(self, key):
        if len(key) == 2:
            x, y = key
            return x in range(len(self.data[0])) and y in range(len(self.data))
        else:
            return False

    def __getitem__(self, key):
        x, y = key
        return self.data[y][x]

    def __setitem__(self, key, value):
        x, y = key
        if not value:
            self.data[y][x] = default_item()
            return
        text, (w, h) = value
        assert isinstance(text, str) and isinstance(w, int) and isinstance(h, int)
        self.data[y][x] = value


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
            self.data[n].insert(newpos, oldpos)

#TODO
#    def copy_row(self, oldpos, newpos):
#        self.data.insert(newpos, oldpos)
#
#    def copy_col(self, oldpos, newpos):
#        for n in range(len(self.data)):
#            x = self.data[n].pop(oldpos)
#            self.data[n].insert(newpos, x)

    def row(self, pos):
        return self.data[pos]

    def col(self, pos):
        return [x[pos] for x in self.data]
