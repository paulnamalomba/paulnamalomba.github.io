# Memory Management and Execution on Windows — C# (.NET)

**Last updated**: December 13, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>

- SESKA Computational Engineer<br>
- SEAT Backend Developer<br>
- Software Developer<br>
- PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Language: C#](https://img.shields.io/badge/Language-C%23-blue.svg)](https://learn.microsoft.com/dotnet/csharp/)
[![Runtime: .NET](https://img.shields.io/badge/Runtime-.NET-512BD4.svg)](https://learn.microsoft.com/dotnet/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

This guide explains how C# and the .NET runtime (CoreCLR/CLR) implement memory management and execution semantics on Windows. Covering value vs reference types, stack vs heap storage, copy semantics, and nullability features (nullable reference types, `Nullable<T>`), plus examples and best practices.

## Contents

- [Memory Management and Execution on Windows — C# (.NET)](#memory-management-and-execution-on-windows--c-net)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Windows — Build \& Run (PowerShell / Command Prompt)](#windows--build--run-powershell--command-prompt)
  - [Overview](#overview-1)
  - [Contents](#contents-1)
  - [1) Data Structures — Value-Type vs Reference-Type](#1-data-structures--value-type-vs-reference-type)
  - [2) Storage — Stack vs Heap \& Garbage Collector](#2-storage--stack-vs-heap--garbage-collector)
  - [3) Copy Semantics — Shallow vs Deep](#3-copy-semantics--shallow-vs-deep)
  - [4) Nullability](#4-nullability)
  - [Examples — Runnable Snippets](#examples--runnable-snippets)
  - [Windows/.NET Specific Notes](#windowsnet-specific-notes)
  - [References](#references)

---

## Windows — Build & Run (PowerShell / Command Prompt)

- Create project and run (dotnet SDK required):

  ```powershell
  # Create console project
  dotnet new console -n MemoryDemo
  cd MemoryDemo
  # Replace Program.cs with main.cs if needed, then run
  dotnet run
  ```

- To build and run specific file you can create `Program.cs` with `Main` method and run `dotnet run` in the project directory.

---

## Overview

This guide explains how C# and the .NET runtime (CoreCLR/CLR) implement memory management and execution semantics on Windows. Covering value vs reference types, stack vs heap storage, copy semantics, and nullability features (nullable reference types, `Nullable<T>`), plus examples and best practices.

---

## Contents

- Data Structures: value types (`struct`) vs reference types (`class`)
- Storage: stack vs heap under CLR; GC generations and finalizers
- Copy semantics: shallow vs deep, `ICloneable`, copy constructors
- Nullability: `null`, nullable reference types, `Nullable<T>`
- Examples & Best Practices
- Windows/.NET specific notes

---

## 1) Data Structures — Value-Type vs Reference-Type

- Value types: primitives (`int`, `double`), `struct`, `enum`. Stored inline where declared (stack or inside objects). Passed by value by default.
- Reference types: `class`, `interface`, `delegate`, `object`, arrays — variables hold a reference to the object on the managed heap.

Table comparison:

| Aspect      | Value Types                | Reference Types                                               |
| ----------- | -------------------------- | ------------------------------------------------------------- |
| Examples    | `int`, `struct Point`      | `class Person`, `string`                                      |
| Storage     | Inline (stack or embedded) | Managed heap (GC)                                             |
| Passing     | Copy of value              | Copy of reference                                             |
| Nullability | `Nullable<T>` (`int?`)     | Can be null, but nullable reference types provide annotations |

Example:

```csharp
struct Point { public int X; public int Y; }
class Person { public string Name { get; set; } }

void Demo() {
    Point p1 = new Point { X = 1, Y = 2 };
    Point p2 = p1; // copy

    Person a = new Person { Name = "Paul" };
    Person b = a; // reference copy
    b.Name = "Changed"; // a.Name == "Changed"
}
```

Notes:

- `string` is a reference type but immutable: assignment yields reference copy; modifications produce new strings.

---

## 2) Storage — Stack vs Heap & Garbage Collector

- CLR allocates value types on the stack (for local variables) or inline within objects. Reference type instances allocated on managed heap.
- Garbage Collector: generational (Gen0/Gen1/Gen2), background GC, server GC. GC reclaims unreachable objects; finalizers (`~Type()`) run on separate finalizer thread.

Windows/.NET specifics:

- The CLR uses the OS virtual memory and the GC has options (Workstation vs Server) and settings in `runtimeconfig.json`.
- Use `GC.Collect` only in rare cases; prefer letting runtime manage memory.

Example demonstrating GC behavior:

```csharp
class Demo {
    static void CreateObjects() {
        for (int i=0;i<100000;i++) {
            var o = new object();
        }
    }

    static void Main() {
        CreateObjects();
        GC.Collect(); // forces collection (not usually recommended)
    }
}
```

Tips:

- Implement `IDisposable` and `using` for deterministic unmanaged resource cleanup.
- Use `WeakReference<T>` for cache-like scenarios where you don't want to keep objects alive.

---

## 3) Copy Semantics — Shallow vs Deep

- Assigning reference variables copies the reference (shallow).
- For deep copy, implement cloning (manual or `ICloneable`) or serialization-based copy.
- Value types are copied by value (deep copy of fields).

Example (shallow vs deep):

```csharp
class Book { public string Title; public List<string> Authors = new(); }

void Demo() {
    var b1 = new Book { Title = "A", Authors = new List<string>{"X"} };
    var b2 = b1; // shallow (reference copy)
    b2.Authors.Add("Y"); // b1.Authors also changed

    // Deep copy (manual)
    var b3 = new Book { Title = b1.Title, Authors = new List<string>(b1.Authors) };
}
```

Best practices:

- Prefer immutable types or make deep copies when necessary.
- Use `MemberwiseClone` carefully; implement custom cloning when needed.

---

## 4) Nullability

- C# supports `null` for reference types; C#8 introduced nullable reference types (`string?`) and static analysis to reduce null-related bugs.
- `Nullable<T>` (`int?`) wraps value types to allow null.

Example:

```csharp
#nullable enable
string? maybe = null;
if (maybe != null) Console.WriteLine(maybe.Length);

int? maybeInt = null;
if (maybeInt.HasValue) Console.WriteLine(maybeInt.Value);
```

Tips:

- Enable nullable reference types in `csproj` (`<Nullable>enable</Nullable>`).
- Use null-coalescing `??` and `?.` for safe access.

---

## Examples — Runnable Snippets

`Program.cs`:

```csharp
using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        // Value vs Reference
        var p1 = new Point { X = 1, Y = 2 };
        var p2 = p1; // copied

        var book1 = new Book { Title = "C#" };
        var book2 = book1; // reference copy
        book2.Title = "Changed";
        Console.WriteLine(book1.Title); // "Changed"

        // Nullable
        string? s = null;
        Console.WriteLine(s ?? "(null)");
    }
}

struct Point { public int X; public int Y; }
class Book { public string Title; public List<string> Authors = new(); }
```

Run with `dotnet run` in project folder.

---

## Windows/.NET Specific Notes

- Tuning GC settings: `DOTNET_gcServer`, `DOTNET_gcConcurrent` environment variables.
- Memory dumps: use `dotnet-dump`, `procdump`, `WinDbg` for post-mortem analysis.
- Use `dotnet-gcdump` and `dotnet-trace` for diagnostics.

---

## References

- Microsoft docs: https://learn.microsoft.com/dotnet/
- .NET GC: https://learn.microsoft.com/dotnet/standard/garbage-collection/

_End of C# guide._
