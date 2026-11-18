# Language runtimes: memory, architectures, and execution

<br>
Last updated: February 26, 2026<br>
Author: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
Contact: [kabwenzenamalomba@gmail.com](mailto:kabwenzenamalomba@gmail.com)<br>
Website: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>
[![C++](https://img.shields.io/badge/Language-C++17-blue.svg)](https://isocpp.org/)
[![C#](https://img.shields.io/badge/Language-C%23_11.0-purple.svg)](https://learn.microsoft.com/en-us/dotnet/csharp/)
[![Python](https://img.shields.io/badge/Language-Python_3.11-yellow.svg)](https://python.org/)

## Overview

A language's runtime determines how it manages memory and how applications are deployed. This guide compares native C++ binaries, garbage collection in the C# .NET Common Language Runtime (CLR), and Python's interpreter and Global Interpreter Lock (GIL).

## Contents

- [Language runtimes: memory, architectures, and execution](#language-runtimes-memory-architectures-and-execution)
  - [Overview](#overview)
  - [Contents](#contents)
  - [1. Configuration (Windows \& Linux)](#1-configuration-windows--linux)
    - [C++ (native compilation)](#c-native-compilation)
    - [C# .NET (managed runtime)](#c-net-managed-runtime)
    - [Python (interpreted virtual machine)](#python-interpreted-virtual-machine)
  - [2. Writing basic Code/scripts (memory operations)](#2-writing-basic-codescripts-memory-operations)
    - [C++: manual memory management](#c-manual-memory-management)
    - [C# .NET: garbage collected (GC)](#c-net-garbage-collected-gc)
    - [Python: reference counting \& the GIL](#python-reference-counting--the-gil)
  - [3. Compile-time commands (compilers vs VMs)](#3-compile-time-commands-compilers-vs-vms)
    - [C++: native binaries](#c-native-binaries)
    - [C# .NET: intermediate language (IL)](#c-net-intermediate-language-il)
    - [Python: bytecode caching](#python-bytecode-caching)
  - [4. Runtime commands (execution contexts)](#4-runtime-commands-execution-contexts)
    - [C++ native execution](#c-native-execution)
    - [.NET Core runtime](#net-core-runtime)
    - [Python VM](#python-vm)
  - [5. Debugging (segfaults vs overflows)](#5-debugging-segfaults-vs-overflows)
    - [C++: the segmentation fault](#c-the-segmentation-fault)
    - [C#: StackOverflows \& GC pauses](#c-stackoverflows--gc-pauses)
    - [Python: the resource bottleneck](#python-the-resource-bottleneck)

---

## 1. Configuration (Windows & Linux)

Setting up an environment depends heavily on how close to the hardware the language operates.

### C++ (native compilation)

C++ compilers generate raw machine code.

```bash
# Linux: Install the GNU Compiler Collection (GCC) and Make
sudo apt install build-essential gdb

# Windows: Install MSVC via Visual Studio Build Tools, or MinGW
```

- **Variables:** The `LD_LIBRARY_PATH` (Linux) or `PATH` (Windows) must explicitly expose your `.so` or `.dll` shared libraries, otherwise the binary will crash instantly at launch.

### C# .NET (managed runtime)

C# compiles to Intermediate Language (IL) targeting the .NET Core / 8/9+ cross-platform runtime.

```bash
# Linux/Windows: Install the official cross-platform .NET SDK
dotnet --version
```

### Python (interpreted virtual machine)

Python requires an interpreter to read source code line-by-line via the Python Virtual Machine.

```bash
sudo apt install python3 python3-venv
python3 --version
```

---

## 2. Writing basic Code/scripts (memory operations)

The foundational difference between these languages is who holds responsibility for cleaning up heap memory after a function completes.

### C++: manual memory management

In C++, invoking the `new` keyword reserves physical RAM bytes. It is entirely the developer's responsibility to delete those bytes. Failing to release the allocation causes a memory leak.

```cpp
#include <iostream>

void processRawData() {
    // Manually allocating 1 million bytes on the heap
    char* buffer = new char[1000000];

    /* System logic utilizing buffer */

    // Developer MUST manually release memory back to the Operating System
    delete[] buffer;
}
```

_Modern architecture favors Smart Pointers (`std::unique_ptr`) automatically triggering destruction via Reference Counting, mitigating human-induced leaks._

### C# .NET: garbage collected (GC)

C# .NET abstracts raw memory. The CLR allocates objects inside Managed Memory heaps. When an object loses all references, the Garbage Collector periodically suspends execution, crawls the heap, and destroys orphaned objects automatically.

```csharp
public void ProcessData() {
    // The CLR handles heap allocation.
    byte[] buffer = new byte[1000000];

    /* System logic utilizing buffer */

    // No explicit delete. The .NET Garbage Collector will free this byte array
    // when 'buffer' falls out of scope and memory pressure rises.
}
```

### Python: reference counting & the GIL

CPython exposes a C-based runtime. Memory is handled automatically via Reference Counting. When a variable's reference count drops to 0, Python instantly frees it.

Python execution is constrained by the Global Interpreter Lock (GIL), a mutex preventing multiple OS threads from executing Python bytecodes concurrently, forcing multithreading to behave sequentially on a single CPU core.

```python
def process_data():
    # Python VM handles the C-level memory allocation
    buffer = bytearray(1000000)
    # Automatically freed via reference decrementing when function exits
```

---

## 3. Compile-time commands (compilers vs VMs)

The build phase prepares the code for its specific runtime context.

### C++: native binaries

C++ directly translates source text into Assembly and finally Binary Machine Code targeted strictly for the physical CPU architecture (x86, ARM).

```bash
# Compiling for an x86 Linux machine
g++ -O3 -o server_binary main.cpp
```

_A binary compiled on Linux will absolutely not run on Windows._

### C# .NET: intermediate language (IL)

C# translates source into a generic bytecode known as MSIL. This is portable across OS architectures.

```bash
# Generates cross-platform .dll bytecodes
dotnet build --configuration Release
```

_At runtime, the .NET CLR detects the host OS and Just-In-Time (JIT) compiles the IL into native machine code._

### Python: bytecode caching

Python uses an interpreter. It skips explicit compilation entirely, though it automatically generates `.pyc` bytecode caches to speed up subsequent load times.

```bash
# Pure execution, compilation phase is implicit
python3 my_script.py
```

---

## 4. Runtime commands (execution contexts)

How these programs are daemonized dictates their scaling capabilities.

### C++ native execution

The binary runs directly against the OS Kernel. Interaction is blistering fast but highly unforgiving.

```bash
# Run directly as an OS process
./server_binary &
```

### .NET Core runtime

The `dotnet` executable creates the CLR environment, loads the application `.dll`, tracks garbage collection generations (Gen0, Gen1, Gen2), and controls JIT compilation.

```bash
# The runtime executes the intermediate DLL
dotnet run --project API/API.csproj
```

### Python VM

The python interpreter boots, allocates memory, locks the GIL, and incrementally interprets logic. For heavy CPU tasks, true parallelism requires Multi-processing (spawning separate Python interpreters) rather than multi-threading.

```bash
# Using Gunicorn to spawn multiple distinct Python process workers
gunicorn app:main -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 5. Debugging (segfaults vs overflows)

Each architecture's failure mode reflects its memory design.

### C++: the segmentation fault

Attempting to read or write memory you haven't explicitly asked the OS for invokes a Kernel panic, crashing the process immediately.

- **The Tools:** `gdb` (GNU Debugger) and `valgrind`. Valgrind tracks memory allocations through a virtual CPU to locate memory leaks.

```bash
valgrind --leak-check=full ./server_binary
```

### C#: StackOverflows & GC pauses

While memory leaks are rare, keeping a reference to an object in a static dictionary permanently prevents the Garbage Collector from freeing it—an effective memory leak.

- **The Pitfall:** The CLR guarantees memory safety, but recursively calling functions endlessly exhausts the strictly constrained frame `Stack`, crashing the runtime via a `StackOverflowException`.
- **The Tools:** PerfView or the Visual Studio Diagnostic Tools to analyze Gen2 Garbage Collection pauses.

### Python: the resource bottleneck

Python rarely crashes the OS (because standard memory violations are caught safely by the interpreter). The danger lies in loading a large pandas DataFrame that exceeds RAM, prompting the OS OOM (Out Of Memory) Killer to terminate the `python3` process.

- **The Tools:** Utilizing `cProfile` to determine exactly which line is trapping the GIL and blocking event loops.

```bash
python3 -m cProfile -s cumtime my_script.py
```
