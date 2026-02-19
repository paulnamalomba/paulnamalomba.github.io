# Memory Management and Execution on Windows — C++ (MSVC)

**Last updated**: December 13, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Language: C++](https://img.shields.io/badge/Language-C%2B%2B-blue.svg)](https://learn.microsoft.com/cpp)
[![Compiler: MSVC](https://img.shields.io/badge/Compiler-MSVC-0078D7.svg)](https://learn.microsoft.com/cpp/build/overview-of-the-microsoft-cpp-compiler)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview 

This guide explains how C++ (MSVC on Windows) handles key memory and execution concepts: value vs reference semantics, stack vs heap storage, copy semantics (deep vs shallow), and nullability. The content focuses on what actually happens under the hood on Windows using MSVC, with short, runnable examples and Windows-specific notes.

## Contents

- [Memory Management and Execution on Windows — C++ (MSVC)](#memory-management-and-execution-on-windows--c-msvc)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Windows — Compile \& Run (Developer Command Prompt / PowerShell)](#windows--compile--run-developer-command-prompt--powershell)
  - [Overview](#overview-1)
  - [Contents](#contents-1)
  - [1) Data Structures — Value-Type vs Reference-Type](#1-data-structures--value-type-vs-reference-type)
  - [2) Storage — Stack vs Heap](#2-storage--stack-vs-heap)
  - [3) Copy Semantics — Shallow vs Deep \& Move Semantics](#3-copy-semantics--shallow-vs-deep--move-semantics)
  - [4) Nullability](#4-nullability)
  - [Examples — Small Runnable Snippets](#examples--small-runnable-snippets)
  - [Windows / MSVC Specific Notes and Pitfalls](#windows--msvc-specific-notes-and-pitfalls)
  - [References](#references)

---

## Windows — Compile & Run (Developer Command Prompt / PowerShell)

Notes: Use the "Developer Command Prompt for VS" (recommended) which sets up MSVC environment variables. If using PowerShell, run the `vcvarsall.bat` script from your Visual Studio installation first.

- Developer Command Prompt (cmd.exe):

  ```cmd
  REM open "Developer Command Prompt for VS"
  cl /EHsc main.cpp /Fe:main.exe
  main.exe
  ```

- PowerShell (example, adjust path to match your VS install):

  ```powershell
  & 'C:\Program Files (x86)\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat' x64
  cl.exe /EHsc main.cpp /Fe:main.exe
  .\main.exe
  ```

- Notes: `/EHsc` enables C++ exception handling model, optimize flags as needed (`/O2`).

---

## Overview

This guide explains how C++ (MSVC on Windows) handles key memory and execution concepts: value vs reference semantics, stack vs heap storage, copy semantics (deep vs shallow), and nullability. The content focuses on what actually happens under the hood on Windows using MSVC, with short, runnable examples and Windows-specific notes.

---

## Contents

- Data Structures: value-types vs reference-types
- Storage: stack vs heap (allocation, lifetime)
- Copy Semantics: shallow vs deep copying, move semantics
- Nullability: `nullptr`, raw pointers, smart pointers, `std::optional`
- Examples & Best Practices
- Windows / MSVC specific notes and pitfalls

---

## 1) Data Structures — Value-Type vs Reference-Type

C++ does not have a single runtime-managed split of "value vs reference" like some managed languages. Instead:

- Primitive built-in types and user-defined `struct` / `class` objects are by default value types (their semantics depend on how you use them).
- An actual *reference type* in C++ is a reference (`T&`) or pointer (`T*`) — these are not objects themselves but aliases or addresses referring to other objects.

Key points:
- Declaring an object `MyType x;` instantiates a value object. If you use `MyType* p = new MyType();` you allocate an object on the heap and `p` stores its address.
- `struct` vs `class` in C++ differ only by default access (public vs private).

Example:

```cpp
struct Point { int x; int y; };

void example() {
    Point a{1,2};        // value: object `a` exists directly
    Point b = a;         // copy constructed (value copy)

    Point* ph = new Point{3,4}; // heap allocation
    delete ph;                 // must free
}
```

Notes/Tips:
- Value semantics by default makes copying cheap for small objects but expensive for large ones.
- Use pointers/references for polymorphism and dynamic lifetime control.

---

## 2) Storage — Stack vs Heap

Where objects live depends on how they are created:

- Stack (automatic storage): local variables defined without `new` inside a function are typically placed on the stack (or may be optimized into registers). Stack allocation is fast and automatically freed when the function returns.
- Heap (dynamic storage): `new`/`malloc` allocate memory on the heap. Heap allocations are relatively slow and the programmer (or RAII wrappers) must free them.

Windows/MSVC specifics:
- MSVC uses the OS virtual memory APIs for heap allocation; default CRT heap allows fragmentation handling, low-fragmentation heap options exist for production (LFH).
- Stack size is configurable per-thread (default ~1MB for Windows threads created by the runtime). Watch recursion and large stack arrays.

Example:

```cpp
void foo() {
    int stackArray[1024]; // on the stack
    int* heapArray = new int[1024]; // on the heap
    // ...
    delete[] heapArray; // free heap memory
}
```

Pitfalls:
- Stack overflow if you allocate huge local arrays or have deep recursion.
- Memory leaks if `delete` not called or exceptions bypass cleanup. Use RAII and smart pointers.

---

## 3) Copy Semantics — Shallow vs Deep & Move Semantics

C++ copy semantics are controlled by copy constructor and assignment operator. By default the compiler-generated copy is a member-wise copy (shallow copy of fields).

- Shallow copy: copies pointer values — both objects point to same memory (danger if both manage lifetime).
- Deep copy: allocate new internal storage and copy the content — safer for ownership transfer.
- Move semantics (C++11+): `std::move` and move constructors/operators enable ownership transfer without expensive deep copies.

Example (shallow vs deep):

```cpp
struct Buffer {
    size_t size;
    char* data;

    // default shallow copy (compiler-generated)
    // custom deep copy
    Buffer(const Buffer& other) : size(other.size) {
        data = new char[size];
        std::memcpy(data, other.data, size);
    }

    // move constructor (steal ownership)
    Buffer(Buffer&& other) noexcept : size(other.size), data(other.data) {
        other.data = nullptr; other.size = 0;
    }

    ~Buffer() { delete[] data; }
};
```

Best practices:
- Prefer RAII containers (`std::vector`, `std::string`) which implement deep/move semantics correctly.
- Implement move operations for expensive-to-copy resources.
- Rule of five / zero: if you implement destructor/copy/move, follow the rule of five (or prefer no manual resource management and rely on standard containers).

---

## 4) Nullability

- The C++ null pointer literal is `nullptr` (C++11+). Raw pointers can be `nullptr`.
- Raw pointers do not express ownership; prefer smart pointers:
  - `std::unique_ptr<T>` for sole ownership; cannot be null-checked for lifetime but can hold `nullptr`.
  - `std::shared_ptr<T>` for shared ownership with ref-counting.
  - `std::weak_ptr<T>` to break cycles.
- `std::optional<T>` represents optional values without heap allocation for inline small types (C++17+).

Example:

```cpp
std::unique_ptr<Foo> p = std::make_unique<Foo>();
if (p) p->Do(); // check for non-null

std::optional<int> maybe;
maybe = 42;
if (maybe.has_value()) { int v = *maybe; }
```

Pitfalls:
- Do not mix `delete` and `delete[]` incorrectly.
- Avoid raw owning pointers; prefer `unique_ptr`/`shared_ptr`.
- Beware of `shared_ptr` cycles causing leaks — use `weak_ptr` to break cycles.

---

## Examples — Small Runnable Snippets

`main.cpp`:

```cpp
#include <iostream>
#include <memory>
#include <optional>
#include <vector>

struct Node { int val; std::unique_ptr<Node> next; };

int main() {
    // Stack vs Heap
    int stackValue = 10;                 // stack
    auto heapValue = std::make_unique<int>(20); // heap via unique_ptr
    std::cout << "stack: " << stackValue << " heap: " << *heapValue << "\n";

    // Deep vs shallow through vectors
    std::vector<int> a = {1,2,3};
    auto b = a; // deep copy (vector owns its memory) but shallow for elements that are pointers

    // Move
    auto c = std::move(a); // a is now empty, c has data without copying

    // Optional
    std::optional<int> maybe;
    maybe = 100;
    if (maybe) std::cout << "maybe: " << *maybe << "\n";

    return 0;
}
```

Compile & run with MSVC as described earlier.

---

## Windows / MSVC Specific Notes and Pitfalls

- Stack size: default thread stack ~1MB. Use `/F` linker option to change stack size if needed.
- Heap performance: Windows has low-fragmentation heap options; CRT debug heap introduces overhead — test release builds for performance.
- Enable security checks: use `/GS`, buffer security mitigations and enable `/RTC` for runtime checks in debug.
- Use `/MD` or `/MT` consistently for runtime library selection (DLL vs static CRT).
- Use AddressSanitizer (ASan) in MSVC (available in modern toolchains) for detecting memory issues.

---

## References

- Microsoft C++ docs: https://learn.microsoft.com/cpp
- C++ Core Guidelines: https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines
- Herb Sutter et al. Resources on move semantics and RAII

---

*End of C++ guide.*
