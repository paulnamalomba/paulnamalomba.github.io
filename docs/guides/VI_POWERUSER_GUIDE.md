# VI/VIM power user guide

**Last updated**: December 12, 2025
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>

- SESKA Computational Engineer<br>
- SEAT Backend Developer<br>
- Software Developer<br>
- PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Editor: Vi/Vim](https://img.shields.io/badge/Editor-Vi%2FVim-2C4F4F.svg)](https://www.vim.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

This Vi/Vim guide covers advanced navigation, editing commands, and customization for working efficiently with text files.

# Contents

- [VI/VIM power user guide](#vivim-power-user-guide)
  - [Overview](#overview)
- [Contents](#contents)
  - [Mode system](#mode-system)
  - [Basic navigation](#basic-navigation)
    - [Character movement](#character-movement)
    - [Word movement](#word-movement)
    - [Line movement](#line-movement)
  - [Advanced navigation](#advanced-navigation)
    - [Screen movement](#screen-movement)
    - [Scrolling](#scrolling)
    - [File movement](#file-movement)
    - [Jump commands](#jump-commands)
    - [Marks](#marks)
  - [Searching](#searching)
    - [Basic search](#basic-search)
    - [Search options](#search-options)
  - [Editing commands](#editing-commands)
    - [Insert mode](#insert-mode)
    - [Delete commands](#delete-commands)
    - [Copy (yank) commands](#copy-yank-commands)
    - [Paste commands](#paste-commands)
    - [Undo/redo](#undoredo)
  - [Visual mode](#visual-mode)
    - [Entering Visual mode](#entering-visual-mode)
    - [Visual mode operations](#visual-mode-operations)
  - [Text objects](#text-objects)
    - [Inner vs around](#inner-vs-around)
    - [Paired objects](#paired-objects)
  - [Command-Line mode (ex commands)](#command-line-mode-ex-commands)
    - [File operations](#file-operations)
    - [Line numbers and ranges](#line-numbers-and-ranges)
    - [Search and replace](#search-and-replace)
    - [Multiple files](#multiple-files)
    - [Windows (splits)](#windows-splits)
    - [Tabs](#tabs)
  - [Advanced features](#advanced-features)
    - [Macros](#macros)
    - [Registers](#registers)
    - [Folding](#folding)
    - [Indentation](#indentation)
    - [Case manipulation](#case-manipulation)
    - [Increment/decrement numbers](#incrementdecrement-numbers)
  - [Configuration](#configuration)
    - [Settings](#settings)
    - [Common settings](#common-settings)
  - [Power user combinations](#power-user-combinations)
    - [Quick navigation patterns](#quick-navigation-patterns)
    - [Efficient editing](#efficient-editing)
    - [Multiple operations](#multiple-operations)
    - [Complex commands](#complex-commands)
  - [Cheat sheet quick reference](#cheat-sheet-quick-reference)
    - [Essential commands](#essential-commands)
    - [Speed tips](#speed-tips)
  - [Help system](#help-system)

---

## Mode system

Vi/Vim operates in different modes:

- **Normal Mode** (Command Mode) - Default mode for navigation and commands
- **Insert Mode** - For typing text
- **Visual Mode** - For selecting text
- **Command-Line Mode** - For executing ex commands

Press `Esc` to return to Normal Mode from any other mode.

---

## Basic navigation

### Character movement

| Command    | Action                   |
| ---------- | ------------------------ |
| `h`        | Move left one character  |
| `j`        | Move down one line       |
| `k`        | Move up one line         |
| `l`        | Move right one character |
| Arrow keys | Also work for movement   |

### Word movement

| Command | Action                                                    |
| ------- | --------------------------------------------------------- |
| `w`     | Move forward to start of next word                        |
| `W`     | Move forward to start of next WORD (whitespace-delimited) |
| `e`     | Move forward to end of word                               |
| `E`     | Move forward to end of WORD                               |
| `b`     | Move backward to start of word                            |
| `B`     | Move backward to start of WORD                            |
| `ge`    | Move backward to end of previous word                     |
| `gE`    | Move backward to end of previous WORD                     |

### Line movement

| Command   | Action                                                 |
| --------- | ------------------------------------------------------ |
| `0`       | Move to beginning of line (column 0)                   |
| `^`       | Move to first non-blank character of line              |
| `$`       | Move to end of line                                    |
| `g_`      | Move to last non-blank character of line               |
| `         | `                                                      | Move to column 0 |
| `5        | `                                                      | Move to column 5 |
| `f{char}` | Move forward to next occurrence of {char} on line      |
| `F{char}` | Move backward to previous occurrence of {char} on line |
| `t{char}` | Move forward to character before next {char}           |
| `T{char}` | Move backward to character after previous {char}       |
| `;`       | Repeat last f, F, t, or T command forward              |
| `,`       | Repeat last f, F, t, or T command backward             |

---

## Advanced navigation

### Screen movement

| Command | Action                                  |
| ------- | --------------------------------------- |
| `H`     | Move to top of screen (High)            |
| `M`     | Move to middle of screen (Middle)       |
| `L`     | Move to bottom of screen (Low)          |
| `zt`    | Scroll current line to top of screen    |
| `zz`    | Scroll current line to center of screen |
| `zb`    | Scroll current line to bottom of screen |

### Scrolling

| Command  | Action                                     |
| -------- | ------------------------------------------ |
| `Ctrl-f` | Scroll forward one full screen (Page Down) |
| `Ctrl-b` | Scroll backward one full screen (Page Up)  |
| `Ctrl-d` | Scroll down half screen                    |
| `Ctrl-u` | Scroll up half screen                      |
| `Ctrl-e` | Scroll down one line (cursor stays)        |
| `Ctrl-y` | Scroll up one line (cursor stays)          |

### File movement

| Command | Action                       |
| ------- | ---------------------------- |
| `gg`    | Go to first line of file     |
| `G`     | Go to last line of file      |
| `50G`   | Go to line 50                |
| `:50`   | Go to line 50 (command mode) |
| `:$`    | Go to last line              |
| `50%`   | Go to 50% through file       |
| `1G`    | Go to first line             |

### Jump commands

| Command  | Action                                        |
| -------- | --------------------------------------------- |
| `Ctrl-o` | Jump to older position in jump list           |
| `Ctrl-i` | Jump to newer position in jump list           |
| `` ` ``  | Jump to last cursor position                  |
| `''`     | Jump to beginning of last line                |
| `` `[ `` | Jump to beginning of last changed/yanked text |
| `` `] `` | Jump to end of last changed/yanked text       |
| `` `< `` | Jump to beginning of last visual selection    |
| `` `> `` | Jump to end of last visual selection          |
| `g;`     | Jump to position of last change               |
| `g,`     | Jump forward through change list              |

### Marks

| Command  | Action                                   |
| -------- | ---------------------------------------- |
| `ma`     | Set mark 'a' at current position         |
| `` `a `` | Jump to mark 'a'                         |
| `'a`     | Jump to beginning of line with mark 'a'  |
| `:marks` | List all marks                           |
| `mA`     | Set global mark 'A' (works across files) |
| `` `. `` | Jump to position of last change          |
| `` `" `` | Jump to position when last exited file   |

---

## Searching

### Basic search

| Command    | Action                                        |
| ---------- | --------------------------------------------- |
| `/pattern` | Search forward for pattern                    |
| `?pattern` | Search backward for pattern                   |
| `n`        | Repeat search in same direction               |
| `N`        | Repeat search in opposite direction           |
| `*`        | Search forward for word under cursor          |
| `#`        | Search backward for word under cursor         |
| `g*`       | Search forward for partial word under cursor  |
| `g#`       | Search backward for partial word under cursor |

### Search options

| Command          | Action                                      |
| ---------------- | ------------------------------------------- |
| `/pattern/e`     | Search and place cursor at end of match     |
| `/pattern/+2`    | Search and place cursor 2 lines below match |
| `:set ic`        | Ignore case in searches                     |
| `:set noic`      | Case-sensitive searches                     |
| `:set hls`       | Highlight search matches                    |
| `:noh`           | Clear search highlighting                   |
| `:set incsearch` | Incremental search (search as you type)     |

---

## Editing commands

### Insert mode

| Command | Action                                        |
| ------- | --------------------------------------------- |
| `i`     | Insert before cursor                          |
| `I`     | Insert at beginning of line                   |
| `a`     | Append after cursor                           |
| `A`     | Append at end of line                         |
| `o`     | Open new line below                           |
| `O`     | Open new line above                           |
| `s`     | Substitute character (delete char and insert) |
| `S`     | Substitute line (delete line and insert)      |
| `C`     | Change to end of line                         |
| `cc`    | Change entire line                            |
| `cw`    | Change word                                   |
| `ciw`   | Change inner word                             |
| `ci"`   | Change text inside quotes                     |
| `ci(`   | Change text inside parentheses                |
| `cit`   | Change text inside HTML/XML tag               |

### Delete commands

| Command    | Action                                  |
| ---------- | --------------------------------------- |
| `x`        | Delete character under cursor           |
| `X`        | Delete character before cursor          |
| `dw`       | Delete word                             |
| `dW`       | Delete WORD                             |
| `dd`       | Delete line                             |
| `D`        | Delete to end of line                   |
| `d$`       | Delete to end of line                   |
| `d0`       | Delete to beginning of line             |
| `dgg`      | Delete to beginning of file             |
| `dG`       | Delete to end of file                   |
| `d50G`     | Delete to line 50                       |
| `dt{char}` | Delete until {char}                     |
| `df{char}` | Delete including {char}                 |
| `diw`      | Delete inner word                       |
| `di"`      | Delete inside quotes                    |
| `da"`      | Delete around quotes (including quotes) |
| `dap`      | Delete around paragraph                 |

### Copy (yank) commands

| Command | Action                    |
| ------- | ------------------------- |
| `yw`    | Yank word                 |
| `yy`    | Yank line                 |
| `Y`     | Yank line (same as yy)    |
| `y$`    | Yank to end of line       |
| `y0`    | Yank to beginning of line |
| `ygg`   | Yank to beginning of file |
| `yG`    | Yank to end of file       |
| `yiw`   | Yank inner word           |
| `yi"`   | Yank inside quotes        |
| `yap`   | Yank around paragraph     |

### Paste commands

| Command | Action                                  |
| ------- | --------------------------------------- |
| `p`     | Paste after cursor/below line           |
| `P`     | Paste before cursor/above line          |
| `gp`    | Paste and move cursor after pasted text |
| `gP`    | Paste before and move cursor            |
| `]p`    | Paste and adjust indentation            |

### Undo/redo

| Command  | Action                   |
| -------- | ------------------------ |
| `u`      | Undo last change         |
| `U`      | Undo all changes on line |
| `Ctrl-r` | Redo                     |
| `.`      | Repeat last change       |
| `&`      | Repeat last :substitute  |

---

## Visual mode

### Entering Visual mode

| Command  | Action                           |
| -------- | -------------------------------- |
| `v`      | Enter character-wise visual mode |
| `V`      | Enter line-wise visual mode      |
| `Ctrl-v` | Enter block-wise visual mode     |
| `gv`     | Reselect last visual selection   |

### Visual mode operations

| Command | Action                            |
| ------- | --------------------------------- |
| `o`     | Move to other end of selection    |
| `O`     | Move to other corner (block mode) |
| `d`     | Delete selection                  |
| `c`     | Change selection                  |
| `y`     | Yank selection                    |
| `>`     | Indent selection                  |
| `<`     | Unindent selection                |
| `=`     | Auto-indent selection             |
| `~`     | Toggle case                       |
| `u`     | Make lowercase                    |
| `U`     | Make uppercase                    |
| `J`     | Join lines                        |

---

## Text objects

Text objects work with operator commands (d, c, y, etc.)

### Inner vs around

| Command | Action                            |
| ------- | --------------------------------- |
| `iw`    | Inner word                        |
| `aw`    | Around word (includes whitespace) |
| `iW`    | Inner WORD                        |
| `aW`    | Around WORD                       |
| `is`    | Inner sentence                    |
| `as`    | Around sentence                   |
| `ip`    | Inner paragraph                   |
| `ap`    | Around paragraph                  |

### Paired objects

| Command              | Action                |
| -------------------- | --------------------- |
| `i"`                 | Inside double quotes  |
| `a"`                 | Around double quotes  |
| `i'`                 | Inside single quotes  |
| `a'`                 | Around single quotes  |
| `` i` ``             | Inside backticks      |
| `` a` ``             | Around backticks      |
| `i(` or `i)` or `ib` | Inside parentheses    |
| `a(` or `a)` or `ab` | Around parentheses    |
| `i{` or `i}` or `iB` | Inside braces         |
| `a{` or `a}` or `aB` | Around braces         |
| `i[` or `i]`         | Inside brackets       |
| `a[` or `a]`         | Around brackets       |
| `i<` or `i>`         | Inside angle brackets |
| `a<` or `a>`         | Around angle brackets |
| `it`                 | Inside tag (HTML/XML) |
| `at`                 | Around tag            |

---

## Command-Line mode (ex commands)

Enter with `:` from Normal mode

### File operations

| Command            | Action                                |
| ------------------ | ------------------------------------- |
| `:w`               | Write (save) file                     |
| `:w filename`      | Save as filename                      |
| `:q`               | Quit                                  |
| `:q!`              | Quit without saving                   |
| `:wq`              | Write and quit                        |
| `:x`               | Write and quit (only if changes)      |
| `ZZ`               | Write and quit (normal mode)          |
| `ZQ`               | Quit without saving (normal mode)     |
| `:e filename`      | Edit (open) file                      |
| `:e!`              | Reload current file (discard changes) |
| `:saveas filename` | Save as and continue editing new file |
| `:r filename`      | Read file and insert below cursor     |
| `:r !command`      | Read command output and insert        |

### Line numbers and ranges

| Command     | Action                     |
| ----------- | -------------------------- |
| `:set nu`   | Show line numbers          |
| `:set nonu` | Hide line numbers          |
| `:set rnu`  | Show relative line numbers |
| `:50`       | Go to line 50              |
| `:$`        | Go to last line            |
| `:+5`       | Go 5 lines down            |
| `:-3`       | Go 3 lines up              |
| `:.`        | Current line               |
| `:%`        | All lines                  |
| `:1,50`     | Lines 1 to 50              |
| `:'a,'b`    | From mark a to mark b      |

### Search and replace

| Command                           | Action                              |
| --------------------------------- | ----------------------------------- |
| `:s/old/new/`                     | Substitute first occurrence on line |
| `:s/old/new/g`                    | Substitute all occurrences on line  |
| `:s/old/new/gc`                   | Substitute with confirmation        |
| `:%s/old/new/g`                   | Substitute in entire file           |
| `:%s/old/new/gi`                  | Substitute case-insensitive         |
| `:5,12s/old/new/g`                | Substitute in lines 5-12            |
| `:'<,'>s/old/new/g`               | Substitute in visual selection      |
| `:g/pattern/d`                    | Delete all lines matching pattern   |
| `:g!/pattern/d` or `:v/pattern/d` | Delete non-matching lines           |
| `:g/pattern/m$`                   | Move matching lines to end          |
| `:g/pattern/t$`                   | Copy matching lines to end          |

### Multiple files

| Command             | Action                            |
| ------------------- | --------------------------------- |
| `:bn`               | Next buffer                       |
| `:bp`               | Previous buffer                   |
| `:bd`               | Delete buffer (close file)        |
| `:ls` or `:buffers` | List buffers                      |
| `:b5`               | Switch to buffer 5                |
| `:b filename`       | Switch to buffer (tab completion) |
| `:ball`             | Open all buffers in windows       |
| `:e#`               | Switch to alternate file          |

### Windows (splits)

| Command          | Action                              |
| ---------------- | ----------------------------------- |
| `:sp filename`   | Split window horizontally           |
| `:vs filename`   | Split window vertically             |
| `Ctrl-w s`       | Split current window horizontally   |
| `Ctrl-w v`       | Split current window vertically     |
| `Ctrl-w q`       | Close current window                |
| `Ctrl-w w`       | Switch to next window               |
| `Ctrl-w h/j/k/l` | Move to window (left/down/up/right) |
| `Ctrl-w H/J/K/L` | Move window to edge                 |
| `Ctrl-w =`       | Make all windows equal size         |
| `Ctrl-w +`       | Increase window height              |
| `Ctrl-w -`       | Decrease window height              |
| `Ctrl-w >`       | Increase window width               |
| `Ctrl-w <`       | Decrease window width               |
| `Ctrl-w _`       | Maximize window height              |
| `Ctrl-w          | `                                   | Maximize window width |

### Tabs

| Command          | Action                 |
| ---------------- | ---------------------- |
| `:tabnew`        | New tab                |
| `:tabe filename` | Edit file in new tab   |
| `:tabc`          | Close current tab      |
| `:tabo`          | Close all other tabs   |
| `gt` or `:tabn`  | Next tab               |
| `gT` or `:tabp`  | Previous tab           |
| `5gt`            | Go to tab 5            |
| `:tabs`          | List all tabs          |
| `:tabm 3`        | Move tab to position 3 |

---

## Advanced features

### Macros

| Command | Action                       |
| ------- | ---------------------------- |
| `qa`    | Record macro in register 'a' |
| `q`     | Stop recording               |
| `@a`    | Execute macro 'a'            |
| `@@`    | Repeat last macro            |
| `5@a`   | Execute macro 'a' 5 times    |
| `qA`    | Append to macro 'a'          |
| `:reg`  | View register contents       |

### Registers

| Command | Action                                |
| ------- | ------------------------------------- |
| `"ayy`  | Yank line into register 'a'           |
| `"ap`   | Paste from register 'a'               |
| `"Ayy`  | Append line to register 'a'           |
| `"+y`   | Yank to system clipboard              |
| `"+p`   | Paste from system clipboard           |
| `"*y`   | Yank to selection clipboard (Linux)   |
| `"*p`   | Paste from selection clipboard        |
| `"0p`   | Paste from yank register (not delete) |
| `"1p`   | Paste from delete register            |
| `:reg`  | View all registers                    |

### Folding

| Command | Action                       |
| ------- | ---------------------------- |
| `zf`    | Create fold (in visual mode) |
| `zf50j` | Create fold for 50 lines     |
| `za`    | Toggle fold                  |
| `zo`    | Open fold                    |
| `zc`    | Close fold                   |
| `zO`    | Open all folds recursively   |
| `zC`    | Close all folds recursively  |
| `zM`    | Close all folds in file      |
| `zR`    | Open all folds in file       |
| `zd`    | Delete fold                  |
| `zE`    | Delete all folds             |

### Indentation

| Command | Action                           |
| ------- | -------------------------------- |
| `>>`    | Indent line                      |
| `<<`    | Unindent line                    |
| `5>>`   | Indent 5 lines                   |
| `>%`    | Indent block (cursor on bracket) |
| `=%`    | Auto-indent block                |
| `gg=G`  | Auto-indent entire file          |
| `=ap`   | Auto-indent paragraph            |
| `==`    | Auto-indent current line         |

### Case manipulation

| Command | Action                   |
| ------- | ------------------------ |
| `~`     | Toggle case of character |
| `g~~`   | Toggle case of line      |
| `gUU`   | Uppercase line           |
| `guu`   | Lowercase line           |
| `gUw`   | Uppercase word           |
| `guw`   | Lowercase word           |
| `gUiw`  | Uppercase inner word     |
| `guiw`  | Lowercase inner word     |

### Increment/decrement numbers

| Command    | Action                           |
| ---------- | -------------------------------- |
| `Ctrl-a`   | Increment number under cursor    |
| `Ctrl-x`   | Decrement number under cursor    |
| `5 Ctrl-a` | Add 5 to number                  |
| `g Ctrl-a` | Increment sequence (visual mode) |

---

## Configuration

### Settings

| Command              | Action                 |
| -------------------- | ---------------------- |
| `:set all`           | Show all settings      |
| `:set`               | Show modified settings |
| `:set option?`       | Show value of option   |
| `:set option`        | Enable boolean option  |
| `:set nooption`      | Disable boolean option |
| `:set option=value`  | Set option value       |
| `:set option+=value` | Append to option       |

### Common settings

```vim
:set number              " Show line numbers
:set relativenumber      " Show relative line numbers
:set ignorecase          " Case-insensitive search
:set smartcase           " Case-sensitive if uppercase used
:set hlsearch            " Highlight search results
:set incsearch           " Incremental search
:set expandtab           " Use spaces instead of tabs
:set tabstop=4           " Tab width
:set shiftwidth=4        " Indent width
:set autoindent          " Auto-indent new lines
:set smartindent         " Smart auto-indent
:set wrap                " Wrap long lines
:set nowrap              " Don't wrap lines
:set mouse=a             " Enable mouse
:set clipboard=unnamed   " Use system clipboard
:set syntax=on           " Enable syntax highlighting
```

---

## Power user combinations

### Quick navigation patterns

```
5j          - Move down 5 lines
10k         - Move up 10 lines
3w          - Move forward 3 words
2b          - Move back 2 words
5G          - Go to line 5
/pattern    - Search forward, then n n n to jump through matches
?pattern    - Search backward
*           - Search word under cursor, use n/N to navigate
```

### Efficient editing

```
ciw         - Change inner word (cursor anywhere in word)
ci"         - Change text inside quotes
ca"         - Change text and quotes
dap         - Delete paragraph
yap         - Yank paragraph
>ap         - Indent paragraph
=ap         - Auto-indent paragraph
gqap        - Format/wrap paragraph
```

### Multiple operations

```
d3w         - Delete 3 words
c2j         - Change current and next 2 lines
y5k         - Yank current and previous 5 lines
5dd         - Delete 5 lines
3p          - Paste 3 times
10i*<Esc>   - Insert 10 asterisks
```

### Complex commands

```
:%s/\s\+$//g              - Remove trailing whitespace
:g/^$/d                   - Delete empty lines
:g/pattern/normal @a      - Execute macro on matching lines
:.,+5s/old/new/g          - Substitute in next 5 lines
:'<,'>normal I#           - Comment visual selection
:%!sort                   - Sort entire file
:r !date                  - Insert current date
```

---

## Cheat sheet quick reference

### Essential commands

- **Exit**: `:q` (quit), `:wq` (save and quit), `:q!` (force quit)
- **Save**: `:w` (write)
- **Navigate**: `h j k l` (left, down, up, right)
- **Go to line**: `:50` or `50G`
- **Go to start**: `gg`
- **Go to end**: `G`
- **Search**: `/pattern` then `n` (next), `N` (previous)
- **Undo**: `u`
- **Redo**: `Ctrl-r`
- **Delete line**: `dd`
- **Copy line**: `yy`
- **Paste**: `p`
- **Insert mode**: `i`
- **Exit insert mode**: `Esc`

### Speed tips

1. Use relative line numbers (`:set rnu`) for quick jumps
2. Use `*` to search word under cursor
3. Use `.` to repeat last change
4. Use text objects: `ciw`, `ci"`, `dap` etc.
5. Record macros for repetitive tasks
6. Use marks (`ma`, `` `a ``) for quick navigation
7. Use `:noh` to clear search highlighting
8. Use `Ctrl-o` and `Ctrl-i` to jump back and forward
9. Use visual block mode (`Ctrl-v`) for column editing
10. Use `:earlier 5m` to go back 5 minutes in undo history

---

## Help system

| Command          | Action                             |
| ---------------- | ---------------------------------- |
| `:help`          | Open help                          |
| `:help topic`    | Help on specific topic             |
| `:help :command` | Help on ex command                 |
| `:help 'option'` | Help on option                     |
| `Ctrl-]`         | Jump to tag under cursor (in help) |
| `Ctrl-o`         | Jump back                          |
| `:q`             | Close help window                  |

**Example help topics:**

- `:help navigation`
- `:help motion`
- `:help text-objects`
- `:help registers`
- `:help patterns`

---

_This guide covers vi/vim commands. Most commands work in both vi and vim, though vim has additional features._
