import csv

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QBrush, QColor, QPen
from PyQt4.QtCore import pyqtSignal, Qt

from libsyntyche.filehandling import FileHandler

from matrix import Matrix


class Scene(QtGui.QWidget, FileHandler):
    print_ = pyqtSignal(str)
    error_sig = pyqtSignal(str)
    prompt_sig = pyqtSignal(str)
    window_title_changed = pyqtSignal(str)

    def __init__(self, config, get_hsbar_pos, get_vsbar_pos):
        super().__init__()
        self.theme = config['theme']

        self.get_hsbar_pos = get_hsbar_pos
        self.get_vsbar_pos = get_vsbar_pos

        self.horizontal_time = False
        self.modified_flag = False
        self.file_path = ''

        self.grid = Matrix()
        self.undo_stack = []

        font = QtGui.QFont(self.theme['font'], self.theme['font size'])
        boldfont = QtGui.QFont(self.theme['font'], self.theme['font size'],
                               weight=QtGui.QFont.Bold)
        self.font_data = {'def': (font, QtGui.QFontMetrics(font)),
                          'bold': (boldfont, QtGui.QFontMetrics(boldfont))}

        self.draw_scene()


    def paintEvent(self, ev):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.scene_image)
        rx, ry = self.get_hsbar_pos(), self.get_vsbar_pos()
        painter.drawPixmap(0, ry, self.header_row)
        painter.drawPixmap(rx, 0, self.header_col)
        painter.drawPixmap(rx, ry, self.corner)

    def draw_scene(self):
        border = self.theme['border']
        row_padding, col_padding = 20, 20
        row_heights = [max([x[1][1] for x in self.grid.row(row) if x[0]] + [0]) + row_padding
                       for row in range(self.grid.count_rows())]
        col_widths = [max([x[1][0] for x in self.grid.col(col) if x[0]] + [0]) + col_padding
                      for col in range(self.grid.count_cols())]

        width = sum(col_widths) + border
        height = sum(row_heights) + border
        self.scene_image = QtGui.QPixmap(width, height)

        # Begin paint
        self.scene_image.fill(QColor(self.theme['background']))
        painter = QtGui.QPainter(self.scene_image)
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        painter.setFont(self.font_data['def'][0])
        painter.setBrush(QColor(self.theme['cell background']))

        # Draw header lines
        hy = int(border + row_heights[0])
        vx = int(border + col_widths[0])
        painter.setPen(QColor(self.theme['details']))
        painter.drawLine(0, hy, border + sum(col_widths), hy)
        painter.drawLine(vx, 0, vx, border + sum(row_heights))

        # Draw border numbers #TODO: fix the offsets
        for n, rh in list(enumerate(row_heights))[1:]:
            painter.drawText(4, border + sum(row_heights[:n]) + rh/2 + 5, str(n))
        for n, cw in list(enumerate(col_widths))[1:]:
            painter.drawText(border + sum(col_widths[:n]) + cw/2 - 5, 16, str(n))

        # Draw plotline lines
        for n, size in enumerate((col_widths, row_heights)[self.horizontal_time]):
            if n == 0: continue
            if self.horizontal_time:
                x, y = col_widths[0]/2, sum(row_heights[:n]) + size/2 - 5
                w, h = sum(col_widths), 10
            else:
                x, y = sum(col_widths[:n]) + size/2 - 5, row_heights[0]/2
                w, h = 10, sum(row_heights)
            painter.fillRect(border + x, border + y, w, h, QColor(self.theme['details']))

        # Draw cells
        painter.setPen(QColor(self.theme['cell border']))
        for r in range(self.grid.count_rows()):
            for c in range(self.grid.count_cols()):
                text, size = self.grid[c,r]
                if not text: continue
                if c == 0 or r == 0:
                    painter.setFont(self.font_data['bold'][0])
                else:
                    painter.setFont(self.font_data['def'][0])
                x = border + sum(col_widths[:c]) + col_widths[c]/2 - size[0]/2
                y = border + sum(row_heights[:r]) + row_heights[r]/2 - size[1]/2
#                painter.drawRoundedRect(x-3, y-3, size[0]+6, size[1]+6, 5, 5)
                painter.drawRect(x-3, y-3, size[0]+6, size[1]+6)
                painter.drawText(x, y, size[0], size[1], Qt.TextWordWrap, text)

        painter.end()

        hw = border + col_widths[0]
        hh = border + row_heights[0]

        self.header_row = self.scene_image.copy(0,0, width, hh)
        self.header_col = self.scene_image.copy(0,0, hw, height)

        self.corner = self.scene_image.copy(0,0, hw, hh)

        self.resize(width, height)
        self.update()


    def prompt(self, text):
        self.prompt_sig.emit(text)

    def error(self, text):
        self.error_sig.emit(text)

    def print_out(self, text):
        self.print_.emit(text)

    # True if orientation is such that rows should be handled
    # False if columns should be handled
    def do_row(self, arg):
        return (self.horizontal_time and arg == 'p') \
            or (not self.horizontal_time and arg == 't')

    def set_time_orientation(self, orientation):
        if orientation not in 'hv':
            self.error('Orientation must be h or v')
            return
        if (orientation == 'h' and self.horizontal_time) or (orientation == 'v' and not self.horizontal_time):
            return
        self.add_undo('flip', None)
        self.grid.flip_orientation()
        self.horizontal_time = not self.horizontal_time
        self.draw_scene()


    # ======== ADD ===========================================================
    def add_plotline(self, name):
        self.insert_plotline(-1, name)

    def add_timeslot(self, name):
        self.insert_timeslot(-1, name)

    # ======== INSERT ========================================================
    def insert_plotline(self, pos, name):
        self._insert(pos, name, 'p')

    def insert_timeslot(self, pos, name):
        self._insert(pos, name, 't')

    def _insert(self, pos, name, arg):
        if self.do_row(arg):
            if pos != -1 and (0,pos-1) not in self.grid:
                self.error('Invalid row')
                return
            self.grid.add_row(pos)
            x, y = 0, pos
            self.add_undo('ir', pos)
        else:
            if pos != -1 and (pos-1,0) not in self.grid:
                self.error('Invalid column')
                return
            self.grid.add_col(pos)
            x, y = pos, 0
            self.add_undo('ic', pos)
        self.set_cell(x, y, name)
        self.draw_scene()

    # ======== MOVE ==========================================================
    def move_plotline(self, oldpos, newpos):
        self._move(oldpos, newpos, 'p')

    def move_timeslot(self, oldpos, newpos):
        self._move(oldpos, newpos, 't')

    def _move(self, oldpos, newpos, arg):
        foldpos, fnewpos = _fix_movepos(oldpos, newpos)
        if self.do_row(arg):
            if (0,oldpos) not in self.grid:
                self.error('Invalid row')
                return
            self.add_undo('mr', (oldpos, newpos))
            self.grid.move_row(foldpos, fnewpos)
        else:
            if (oldpos,0) not in self.grid:
                self.error('Invalid column')
                return
            self.add_undo('mc', (oldpos, newpos))
            self.grid.move_col(foldpos, fnewpos)
        self.draw_scene()

    # ======== COPY ==========================================================
    def copy_plotline(self, oldpos, newpos):
        self._copy(oldpos, newpos, 'p')

    def copy_timeslot(self, oldpos, newpos):
        self._copy(oldpos, newpos, 't')

    def _copy(self, oldpos, newpos, arg):
        foldpos, fnewpos = _fix_movepos(oldpos, newpos)
        if self.do_row(arg):
            if (0,oldpos) not in self.grid:
                self.error('Invalid row')
                return
            self.add_undo('ir', int(newpos))
            self.grid.copy_row(foldpos, fnewpos)
        else:
            if (oldpos,0) not in self.grid:
                self.error('Invalid column')
                return
            if (0,newpos) not in self.grid:
                fnewpos = -1
                #self.add_undo('ic', -1)
            else:
                #self.add_undo('rc', (newpos, self.grid.col(newpos)))
                pass
            #TODO self.grid.copy_col(foldpos, fnewpos)
            self.error('Copy plotline/timeslot not yet implemented')
        self.draw_scene()

    # ======== REMOVE ========================================================
    def remove_plotline(self, pos):
        self._remove(pos, 'p')

    def remove_timeslot(self, pos):
        self._remove(pos, 't')

    def _remove(self, pos, arg):
        if self.do_row(arg):
            if (0,pos) not in self.grid:
                self.error('Invalid row')
                return
            self.add_undo('rr', (pos, self.grid.row(pos)))
            self.grid.remove_row(pos)
        else:
            if (pos,0) not in self.grid:
                self.error('Invalid column')
                return
            self.add_undo('rc', (pos, self.grid.col(pos)))
            self.grid.remove_col(pos)
        self.draw_scene()

    # ======== CELLS =========================================================
    def move_cell(self, x1, y1, x2, y2):
        if not ((x1,y1) in self.grid and (x2,y2) in self.grid):
            self.error('Invalid coordinates')
            return
        if not self.grid[x2,y2][0] == '':
            print_out('Warning: Text overwritten') #TODO Switch to output instead
        self.add_undo('mi', ((x1, y1, self.grid[x1,y1]), (x2, y2, self.grid[x2,y2])))
        self.grid[x2,y2] = self.grid[x1,y1]
        self.grid[x1,y1] = None
        self.draw_scene()

    def copy_cell(self, x1, y1, x2, y2):
        if not ((x1,y1) in self.grid and (x2,y2) in self.grid):
            self.error('Invalid coordinates')
            return
        if not self.grid[x2,y2][0] == '':
            self.print_out('Warning: Text overwritten') #TODO Switch to output instead
        self.add_undo('e', (x2, y2, self.grid[x2,y2]))
        self.grid[x2,y2] = self.grid[x1,y1]
        self.draw_scene()

    def edit_cell(self, x, y, text):
        if (x,y) not in self.grid:
            self.error('Invalid coordinate')
            return
        if not text:
            self.prompt('e{} {} {}'.format(x, y, self.grid[x,y][0]))
            return
        self.add_undo('e', (x, y, self.grid[x,y]))
        self.set_cell(x, y, text)
        self.draw_scene()

    def clear_cell(self, x, y):
        if (x,y) not in self.grid:
            self.error('Invalid coordinate')
            return
        self.add_undo('e', (x, y, self.grid[x,y]))
        self.grid[x,y] = None
        self.draw_scene()

    def set_cell(self, x, y, name):
        if x == 0 and y == 0:
            self.error('Can\'t edit cell 0,0!')
            return
        if x == 0 or y == 0:
            fd = 'bold'
        else:
            fd = 'def'
        name = name.replace('\\n','\n')
        size = self.font_data[fd][1].boundingRect(0,0,150,10000,Qt.TextWordWrap,name).size()
        self.grid[x,y] = (name, (size.width(), size.height()))

    # ======== UNDO ==========================================================
    def add_undo(self, cmd, arg):
        self.modified_flag = True
        self.update_title()
        self.undo_stack.append((cmd, arg))

    def undo(self):
        if not self.undo_stack:
            self.error('Nothing to undo')
            return
        cmd, arg = self.undo_stack.pop()
        # Edit
        if cmd == 'e':
            x, y, item = arg
            self.grid[x,y] = item
        # Move
        elif cmd[0] == 'm':
            if cmd[1] == 'r':
                old, new = _fix_movepos(*arg)
                self.grid.move_row(new, old)
            elif cmd[1] == 'c':
                old, new = _fix_movepos(*arg)
                self.grid.move_col(new, old)
            elif cmd[1] == 'i':
                oldcell, newcell = arg
                x1, y1, item1 = oldcell
                x2, y2, item2 = newcell
                self.grid[x1,y1] = item1
                self.grid[x2,y2] = item2
        # Insert
        elif cmd[0] == 'i':
            if cmd[1] == 'r':
                self.grid.remove_row(arg)
            else:
                self.grid.remove_col(arg)
        # Remove
        elif cmd[0] == 'r':
            pos, arr = arg
            if cmd[1] == 'r':
                self.grid.add_row(pos)
                for n, item in enumerate(arr):
                    self.grid[n,pos] = item
            else:
                self.grid.add_col(pos)
                for n, item in enumerate(arr):
                    self.grid[pos,n] = item
        # Flip orientation
        elif cmd == 'flip':
            self.grid.flip_orientation()
            self.horizontal_time = not self.horizontal_time
        else:
            self.error('Unknown undo: ' + cmd)
            return
        self.draw_scene()

    # ======= FILE NAME =================================================
    def update_title(self):
        title = '{0}{1}{0}'.format('*'*self.modified_flag, self.file_path or 'New file')
        self.window_title_changed.emit(title)

    def set_filename(self, filename=''):
        self.file_path = filename
        self.update_title()

    # ======= FILE HANDLING =============================================
    def is_modified(self):
        return self.modified_flag

    def dirty_window_and_start_in_new_process(self):
        return False #TODO

    def post_new(self):
        self.undo_stack = []
        self.grid.clear()
        self.draw_scene()
        self.modified_flag = False
        self.set_filename()

    def open_file(self, filename):
        text_matrix = []
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.reader(f, dialect='unix', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                text_matrix.append(row)

        if text_matrix[0][0] in ('HORIZONTAL TIME', 'VERTICAL TIME'):
            if text_matrix[0][0] == ['HORIZONTAL TIME']:
                self.horizontal_time = True
            elif text_matrix[0][0] == ['VERTICAL TIME']:
                self.horizontal_time = False
            text_matrix[0][0] = ''

        self.grid.clear()
        for _ in range(len(text_matrix)-1):
            self.grid.add_row()
        for _ in range(len(text_matrix[0])-1):
            self.grid.add_col()
        for rown, row in enumerate(text_matrix):
            for coln, text in enumerate(row):
                if coln == 0 and rown == 0:
                    continue
                self.set_cell(coln, rown, text)
        self.draw_scene()

        self.modified_flag = False
        self.set_filename(filename)
        self.undo_stack = []
        return True

    def write_file(self, filename):
        direction = 'HORIZONTAL TIME' if self.horizontal_time else 'VERTICAL TIME'
        first_row = [direction] + [x[0] for x in self.grid.row(0)[1:]]
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, dialect='unix', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(first_row)
            for row in list(range(self.grid.count_rows()))[1:]:
                writer.writerow([x[0] for x in self.grid.row(row)])

    def post_save(self, saved_filename):
        self.modified_flag = False
        self.set_filename(saved_filename)


def _fix_movepos(oldpos, newpos):
    if newpos == '+':
        newpos = oldpos + 1
    elif newpos == '-':
        newpos = max(oldpos-1, 1)
    elif oldpos < int(newpos):
        newpos = max(int(newpos) - 1, 1)
    return oldpos, int(newpos)
