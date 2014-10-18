urd
===

Plot and organize timelines for novels and stories.



Commands
--------

###Plotline/timeslot handling###
* `a(p|t) <name>` – Add plotline or timeslot.
* `i(p|t) <pos> <name>` – Insert plotline or timeslot at place `<pos>`.
* `r(p|t) <pos>` – Remove plotline or timeslot at place `<pos>`.
* `m(p|t) <oldpos> <newpos>` – Move plotline or timeslot from place `<oldpos>` to just before what plotline/timeslot now is at place `<newpos>`. If `<newpos>` is + or -, the timeslot/plotline will move one position forwards/backwards.

###Cells###
* `e <x> <y>[ <text>]` – Set text in the cell at column `<x>` and row `<y>` to `<text>`. If `<text>` is omitted, the current text in the cell is printed in the terminal for your convenience.
* `d <x> <y>` – Clear cell.
* `mc <x1> <y1> <x2> <y2>` – Move cell from `<x1>`,`<y1>` to `<x2>`,`<y2>`. Cells in row or column 0 can not be moved.
* `c <x1> <y1> <x2> <y2>` – Copy cell at `<x1>`,`<y1>` to `<x2>`,`<y2>`. Cells in row or column 0 can not be copied. WARNING: This will (so far) erase all original data in the target cell.

###Misc###
* `?[<command>]` – List all commands or show help for `<command>`
* `u` – Undo last action. There is no limit to how many undos are saved. The undo stack is reset when a new or existing file is opened.
* `t(h|v)` – Set time orientation to horizontal or vertical. This is the orientation that the plotlines are in (ie. horizontal means that plotlines are rows).

###File handling###
* `n[!]` – Create new file, use `!` to ignore unsaved changes.
* `o[!] <filename>` – Open `<filename>`, use `!` to ignore unsaved changes.
* `s[!] [<filename>]` – Save the opened file, or save to `<filename>`. Use `!` to ignore existing file.
* `q[!]` – Quit, use `!` to ignore unsaved changes.


File format
-----------

Files are saved as csv-files (comma separated values) in the default csv format that LibreOffice uses (at least on Linux). The documentation in python's csv module says:

    > "only quote those fields which contain special characters such as delimiter, quotechar or any of the characters in lineterminator"

Cell 0,0 in saved files contains the orientation of time in the file, either `HORIZONTAL TIME` or `VERTICAL TIME`.