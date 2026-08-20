# Memory Management and Execution on Windows — Python (CPython)

**Last updated**: December 13, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>

- SESKA Computational Engineer<br>
- SEAT Backend Developer<br>
- Software Developer<br>
- PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Language: Python](https://img.shields.io/badge/Language-Python-3776AB.svg)](https://www.python.org/)
[![Interpreter: CPython](https://img.shields.io/badge/Interpreter-CPython-FFD43B.svg)](https://docs.python.org/3/c-api/intro.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

This guide explains how Python (CPython on Windows) handles key memory and execution concepts: value vs reference semantics, heap storage, copy semantics (deep vs shallow), and nullability. The content focuses on what actually happens under the hood on Windows using CPython, with short, runnable examples and Windows-specific notes.

## Contents

- [Memory Management and Execution on Windows — Python (CPython)](#memory-management-and-execution-on-windows--python-cpython)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Windows — Run (PowerShell / Command Prompt)](#windows--run-powershell--command-prompt)
  - [Overview](#overview-1)
  - [Contents](#contents-1)
  - [1) Data Structures — "Value" vs "Reference" in Python](#1-data-structures--value-vs-reference-in-python)
  - [2) Storage — Heap, Object Layout, and CPython Internals](#2-storage--heap-object-layout-and-cpython-internals)
  - [3) Copy Semantics — Shallow vs Deep Copy](#3-copy-semantics--shallow-vs-deep-copy)
  - [4) Nullability — `None` and Safe Usage](#4-nullability--none-and-safe-usage)
  - [Examples — Runnable Snippets](#examples--runnable-snippets)
  - [Windows / CPython Specific Notes](#windows--cpython-specific-notes)
  - [References](#references)

---

## Windows — Run (PowerShell / Command Prompt)

- Run `main.py` with your installed Python interpreter:

  ```powershell
  # PowerShell
  python main.py

  # If multiple versions installed, use py launcher
  py -3 main.py
  ```

- Ensure your PATH includes the Python installation or use the `py` launcher which is installed by default on Windows.

---

## Overview

Python (CPython) provides high-level memory management with automatic memory allocation, reference counting, and a cyclic garbage collector. This guide explains how Python handles value vs reference semantics (always objects), memory allocation (heap-managed objects), copy semantics (shallow vs deep), and nullability (`None`). Examples demonstrate behaviour and best practices for Windows environments.

---

## Contents

- Data Structures: all objects, value vs reference interpretation
- Storage: heap allocation, object layout in CPython, small object allocator
- Copy Semantics: assignment, shallow copy, deep copy
- Nullability: `None` and safety patterns
- Examples & Best Practices
- Windows/CPython specifics

---

## 1) Data Structures — "Value" vs "Reference" in Python

- In Python, _everything is an object_. Names (variables) are labels bound to object references.
- Immutable types (e.g., `int`, `str`, `tuple`) behave like values semantically — operations produce new objects. Mutable types (`list`, `dict`, `set`) allow in-place changes.

Example:

```python
# assignment binds names to objects
a = 10
b = a  # both names point to same int object
b = 20 # b now points to new int object; a unchanged

lst1 = [1,2,3]
lst2 = lst1
lst2.append(4)
print(lst1)  # [1,2,3,4]
```

Notes:

- Understanding mutability is essential: immutable types are safe to share, mutable types require attention.

---

## 2) Storage — Heap, Object Layout, and CPython Internals

- CPython allocates objects on the heap. The interpreter uses a small-object allocator (`pymalloc`) optimized for small objects.
- Each object has a header including reference count and a pointer to type object (`PyObject_HEAD`).
- Memory for large objects (arrays, bytes) is allocated separately.

Reference counting & GC:

- CPython primarily uses reference counting (immediate deallocation when refcount drops to zero).
- It also has a cyclic garbage collector (`gc` module) to detect and collect reference cycles.

Windows specifics:

- CPython uses the Windows heap API under-the-hood; performance tuning is limited compared to native languages.

---

## 3) Copy Semantics — Shallow vs Deep Copy

- Assignment copies references (no object duplication).
- `copy.copy()` performs a shallow copy: top-level container duplicated, inner references copied.
- `copy.deepcopy()` produces deep copy recursively.

Example:

```python
import copy
orig = [[1,2],[3,4]]
shallow = copy.copy(orig)
deep = copy.deepcopy(orig)
orig[0].append(9)
print(shallow) # shares nested lists -> shows change
print(deep)    # independent copy -> no change
```

Tips:

- Prefer immutable objects for safety.
- Use `deepcopy` cautiously — expensive for large structures.

---

## 4) Nullability — `None` and Safe Usage

- `None` is the singleton null value in Python. Any variable can be set to `None`.
- Use `is None` / `is not None` for checks.

Example:

```python
x = None
if x is None:
    print('no value')
```

Pitfalls:

- Do not use `== None`; use `is None` for identity.
- Be careful with mutable default arguments in function signatures; use `None` sentinel.

```python
def append_to(element, to=None):
    if to is None:
        to = []
    to.append(element)
    return to
```

---

## Examples — Runnable Snippets

`main.py`:

```python
import copy

# Data structure behavior
x = 10
y = x
print(x, y)

lst = [1,2]
alias = lst
alias.append(3)
print('alias modifies original:', lst)

# Shallow vs deep copy
orig = [[1],[2]]
shallow = copy.copy(orig)
deep = copy.deepcopy(orig)
orig[0].append(99)
print('shallow:', shallow)
print('deep   :', deep)

# None usage
maybe = None
print('maybe is None ->', maybe is None)
```

Run with `python main.py` or `py -3 main.py` on Windows.

---

## Windows / CPython Specific Notes

- Use `py` launcher to select Python version on Windows.
- CPython's GIL (Global Interpreter Lock) affects multi-threaded CPU-bound programs; prefer multiprocessing for CPU work.
- For native performance, consider C extensions, `cython`, or `multiprocessing`.
- Use `tracemalloc`, `objgraph`, `gc` module for memory diagnostics.

---

## References

- CPython internals: https://github.com/python/cpython
- Python memory management: https://docs.python.org/3/c-api/memory.html
- `gc` module docs: https://docs.python.org/3/library/gc.html

_End of Python guide._
