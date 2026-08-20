# C# Programming — Data Structures, Classes, Coding Style & Language Mechanics

**Last updated**: December 13, 2025  
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>

- SESKA Computational Engineer<br>
- SEAT Backend Developer<br>
- Software Developer<br>
- PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Language: C#](https://img.shields.io/badge/Language-C%23-239120.svg)](https://docs.microsoft.com/dotnet/csharp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

This guide is a comprehensive reference for C# developers covering language fundamentals, data structures (built-in and advanced), classes/objects/modules, coding style, and practical language mechanics. Designed to match the style of existing guides, it provides clear examples, code snippets, tables for comparison, tips, and pitfalls for each major topic.

Use this guide as a reference when designing APIs, choosing data structures, writing idiomatic C#, or preparing for production deployment across .NET platforms.

## Contents

- [C# Programming — Data Structures, Classes, Coding Style \& Language Mechanics](#c-programming--data-structures-classes-coding-style--language-mechanics)
  - [Overview](#overview)
  - [Contents](#contents)
  - [C# Fundamentals](#c-fundamentals)
    - [Compilation \& Runtime](#compilation--runtime)
    - [CLR, JIT \& Memory Management](#clr-jit--memory-management)
    - [Type System (Value vs Reference)](#type-system-value-vs-reference)
  - [Primitive Types \& Built-in Collections](#primitive-types--built-in-collections)
    - [Primitive Types (short summary)](#primitive-types-short-summary)
    - [Arrays](#arrays)
    - [List and Generic Collections](#list-and-generic-collections)
    - [Dictionary, HashSet, Queue, Stack](#dictionary-hashset-queue-stack)
    - [Span and Memory (brief)](#span-and-memory-brief)
  - [Advanced Data Structures](#advanced-data-structures)
    - [Linked Lists](#linked-lists)
    - [Trees and Binary Trees](#trees-and-binary-trees)
    - [Graphs (Adjacency lists/matrices)](#graphs-adjacency-listsmatrices)
    - [Hash Tables \& Collision Strategies](#hash-tables--collision-strategies)
  - [Classes, Objects \& OOP](#classes-objects--oop)
    - [Classes, Structs, Records](#classes-structs-records)
    - [Constructors, Properties, Auto-properties](#constructors-properties-auto-properties)
    - [Inheritance, Interfaces \& Polymorphism](#inheritance-interfaces--polymorphism)
    - [Encapsulation \& Access Modifiers](#encapsulation--access-modifiers)
    - [Design: SRP, DI, SOLID Summary](#design-srp-di-solid-summary)
  - [Modules, Namespaces \& Assemblies](#modules-namespaces--assemblies)
    - [Namespaces \& `using`](#namespaces--using)
    - [Assemblies \& `csproj`](#assemblies--csproj)
    - [NuGet and Versioning](#nuget-and-versioning)
  - [Coding Style \& Conventions](#coding-style--conventions)
    - [Naming, Indentation, Braces, XML docs](#naming-indentation-braces-xml-docs)
    - [Best practices for readability, maintainability \& performance](#best-practices-for-readability-maintainability--performance)
  - [Testing, Debugging \& Tooling](#testing-debugging--tooling)
  - [C# in the Modern .NET Ecosystem](#c-in-the-modern-net-ecosystem)
  - [Appendices — Cheatsheets \& Common Patterns](#appendices--cheatsheets--common-patterns)
    - [Common language idioms](#common-language-idioms)
    - [Common pitfalls checklist](#common-pitfalls-checklist)
  - [References \& Further Reading](#references--further-reading)

---

## C# Fundamentals

### Compilation & Runtime

- C# source (.cs) files are compiled by the C# compiler (`csc` or Roslyn) into Common Intermediate Language (CIL) contained in assemblies (`.dll` or `.exe`).
- Assemblies are metadata-rich and include manifest, type metadata, and IL code.
- At runtime the Common Language Runtime (CLR) loads assemblies, performs Just-In-Time (JIT) compilation of IL to native code, and manages memory via garbage collection.
- .NET versions: .NET Framework (Windows only), .NET Core/.NET (cross-platform modern runtime), Mono (older cross-platform/runtime for mobile).

Key steps:

1. Source (.cs) → Roslyn compiler → IL (assembly)
2. CLR loads assembly, verifies metadata
3. JIT compiles IL methods on first use to native code
4. Execution under CLR with GC, security, and interop

Notes:

- Roslyn provides compiler-as-a-service APIs used by analyzers and IDE tooling.
- Ahead-of-Time (AOT) compilation and ReadyToRun options exist for performance-sensitive scenarios.

### CLR, JIT & Memory Management

- CLR responsibilities: type safety, memory management, security, threading, exception handling and interop.
- JIT compiles IL to native machine code per method; Tiered JIT and AOT (PublishTrimmed, Native AOT) are available in modern .NET.
- Garbage Collector (GC): generational (Gen 0, Gen 1, Gen 2, Large Object Heap) with background and server modes.
- Deterministic disposal: implement `IDisposable` for unmanaged resources and use `using`/`using var` for scope-based disposal.

Memory tips:

- Avoid large allocations on LOH when possible.
- Prefer pooling (`ArrayPool<T>`) for frequently allocated buffers.
- Use `Span<T>`, `Memory<T>` to work with slices without allocations for high-performance workloads.

### Type System (Value vs Reference)

| Aspect         |                          Value Types | Reference Types                                        |
| -------------- | -----------------------------------: | ------------------------------------------------------ |
| Examples       |     `int`, `float`, `struct`, `bool` | `class`, `string`, `object`, arrays, delegates         |
| Storage        |          Stack (or inline in object) | Heap (object referenced by pointer)                    |
| Copy semantics | Copy the value (deep copy of fields) | Copy the reference (shallow copy)                      |
| Nullability    |    Non-nullable (unless nullable T?) | Can be null (nullable reference types in C#8+ enabled) |
| Default        |                     Zero-initialized | `null` reference                                       |

Pitfalls:

- Boxing/unboxing: avoid unnecessary boxing of value types into `object` (performance overhead).
- Structs should be small and immutable; large structs cause copies and performance overhead.

Example:

```csharp
int a = 5;
int b = a; // copy of value
b = 7; // a is still 5

class Node { public int Value; }
var n1 = new Node { Value = 5 };
var n2 = n1; // reference copy
n2.Value = 7; // n1.Value is now 7
```

---

## Primitive Types & Built-in Collections

### Primitive Types (short summary)

- Integral: `byte`, `sbyte`, `short`, `ushort`, `int`, `uint`, `long`, `ulong`
- Floating point: `float`, `double`, `decimal` (decimal for financial high-precision)
- Other: `char`, `bool`, `string` (reference type), `object`
- Nullable value types: `int?`, `DateTime?`

Use `decimal` for money, `double` for scientific, `float` for memory-constrained scenarios.

### Arrays

- Fixed-size, zero-based indexed. Type `T[]`.
- Fast access, contiguous memory for primitive types.

Example:

```csharp
int[] arr = new int[5];
arr[0] = 42;

// Multidimensional
int[,] matrix = new int[3,4];

// Jagged array
int[][] jagged = new int[3][];
jagged[0] = new int[] {1,2};
```

Notes/tips:

- Arrays have `Length`, not `Count`.
- When you need dynamic sizing use `List<T>`.

### List<T> and Generic Collections

- `List<T>` is the go-to dynamic array, it resizes automatically.
- `IList<T>`, `IReadOnlyList<T>` interfaces provide abstraction.

Example:

```csharp
var list = new List<string>();
list.Add("hello");
list.RemoveAt(0);
foreach(var s in list) Console.WriteLine(s);
```

Performance:

- `List<T>` has amortized O(1) append; use `Capacity` property to pre-allocate when size known.

### Dictionary, HashSet, Queue, Stack

- `Dictionary<TKey, TValue>`: hash table mapping keys to values; O(1) average lookup.
- `HashSet<T>`: unique collection based on hashing.
- `Queue<T>`: FIFO, use `Enqueue`/`Dequeue`.
- `Stack<T>`: LIFO, use `Push`/`Pop`.

Example:

```csharp
var dict = new Dictionary<string,int>();
dict["apples"] = 3;
if (dict.TryGetValue("apples", out var val)) Console.WriteLine(val);

var set = new HashSet<int> {1,2,3};
set.Add(2); // ignored, already present

var q = new Queue<string>();
q.Enqueue("a"); var head = q.Dequeue();

var s = new Stack<int>();
s.Push(1); var top = s.Pop();
```

Pitfalls:

- `Dictionary` throws if key not present with indexer; use `TryGetValue`.
- Choose good `Equals`/`GetHashCode` implementations for keys.

### Span<T> and Memory<T> (brief)

- `Span<T>` — stack-only, non-allocating type for contiguous memory slices.
- `Memory<T>` — heap-based, can be awaited and used across async boundaries.

Use in performance-sensitive code to avoid allocations and copying.

Example:

```csharp
Span<byte> buffer = stackalloc byte[256]; // stack memory
// operate on buffer without heap allocation
```

---

## Advanced Data Structures

> This section focuses on building blocks beyond the standard collections: when to implement them and how to use them in C#.

### Linked Lists

- `LinkedList<T>` exists in BCL; implements a doubly-linked list.
- Use when frequent insertions/removals in middle of sequence are required and you have references to nodes.

Example using `LinkedList<T>`:

```csharp
var ll = new LinkedList<int>();
var node = ll.AddLast(1);
ll.AddAfter(node, 2);
ll.Remove(node);
```

Singly-linked list implementation (simple):

```csharp
public class SinglyNode<T> { public T Value; public SinglyNode<T>? Next; }

public class SinglyLinkedList<T>
{
    private SinglyNode<T>? head;
    public void AddFirst(T value) { head = new SinglyNode<T>{ Value = value, Next = head }; }
    public T? RemoveFirst() { if (head == null) return default; var val = head.Value; head = head.Next; return val; }
}
```

Tips:

- Avoid using linked lists for cache-friendly workloads; arrays/Lists are often faster due to contiguous memory.

### Trees and Binary Trees

- Trees are hierarchical structures. Binary trees have up to two children per node.
- Use trees for sorted data, prefix structures (tries), expression parsing, and hierarchical relationships.

Binary search tree (BST) basic example:

```csharp
public class TreeNode<T> where T : IComparable<T>
{
    public T Value; public TreeNode<T>? Left; public TreeNode<T>? Right;
}

public class BinarySearchTree<T> where T : IComparable<T>
{
    private TreeNode<T>? root;
    public void Insert(T value) { root = InsertRec(root, value); }
    private TreeNode<T> InsertRec(TreeNode<T>? node, T value)
    {
        if (node == null) return new TreeNode<T>{ Value = value };
        if (value.CompareTo(node.Value) < 0) node.Left = InsertRec(node.Left, value);
        else node.Right = InsertRec(node.Right, value);
        return node;
    }
}
```

Traversal: In-order (sorted), pre-order, post-order.

Notes:

- Self-balancing trees (AVL, Red-Black) are used in production for predictable performance.
- `SortedSet<T>` and `SortedDictionary<TKey,TValue>` implement tree-based collections in BCL.

### Graphs (Adjacency lists/matrices)

- Graphs represent nodes (vertices) and edges (connections). Use adjacency lists for sparse graphs and adjacency matrix for dense graphs.

Simple graph representation (adjacency list):

```csharp
public class Graph
{
    private readonly Dictionary<int, List<int>> _adj = new();
    public void AddEdge(int u, int v) { if (!_adj.ContainsKey(u)) _adj[u] = new List<int>(); _adj[u].Add(v); }
    public IEnumerable<int> Neighbors(int v) => _adj.TryGetValue(v, out var list) ? list : Enumerable.Empty<int>();
}

// BFS
public IEnumerable<int> BFS(int start)
{
    var visited = new HashSet<int>();
    var q = new Queue<int>();
    q.Enqueue(start); visited.Add(start);
    while (q.Count > 0) {
        var v = q.Dequeue(); yield return v;
        foreach(var n in Neighbors(v)) if (visited.Add(n)) q.Enqueue(n);
    }
}
```

Pitfalls:

- For weighted graphs use Dijkstra/A* algorithms; for negative weights use Bellman-Ford.

### Hash Tables & Collision Strategies

- `Dictionary<TKey,TValue>` is a hash table using buckets; collisions handled via chaining.
- Key design: implement `GetHashCode()` and `Equals()` correctly for custom types.

Example custom key:

```csharp
public struct Point : IEquatable<Point>
{
    public int X { get; }
    public int Y { get; }
    public override int GetHashCode() => HashCode.Combine(X, Y);
    public bool Equals(Point other) => X == other.X && Y == other.Y;
}
```

Note: `HashCode.Combine` is available to make good composite hashes.

---

## Classes, Objects & OOP

### Classes, Structs, Records

- `class` — reference type with identity. Suitable for most domain objects, heavy state, and polymorphism.
- `struct` — value type, stack-allocated (or inlined). Prefer for small immutable types.
- `record` — reference type (in C# 9+) providing value-like equality semantics and concise syntax. Records can also be `record struct`.

Examples:

```csharp
public class Person
{
    public string FirstName { get; set; }
    public string LastName { get; set; }
}

public struct Point { public int X; public int Y; }

public record User(string Username, string Email);
```

When to use what:

- Use `struct` for small (<16 bytes commonly) and immutable types.
- Use `record` for DTOs/immutable data carriers where value equality is desired.

### Constructors, Properties, Auto-properties

```csharp
public class Config
{
    // Auto-property
    public string Name { get; set; }

    // Read-only property with init-only setter (C#9+)
    public string Id { get; init; }

    // Constructor
    public Config(string name) => Name = name;
}
```

Use `private set` or `init` to control mutability.

### Inheritance, Interfaces & Polymorphism

- `:` syntax for inheritance and interface implementation.
- Prefer interfaces for abstractions and loose coupling.
- Use `virtual`/`override` for runtime polymorphism.

Example:

```csharp
public interface IRepository<T> { void Add(T item); }

public abstract class RepositoryBase<T> : IRepository<T>
{
    public abstract void Add(T item);
}

public class MemoryRepository<T> : RepositoryBase<T>
{
    private readonly List<T> _items = new();
    public override void Add(T item) => _items.Add(item);
}
```

Polymorphism example:

```csharp
public class Animal { public virtual string Speak() => "..."; }
public class Dog : Animal { public override string Speak() => "woof"; }

Animal a = new Dog(); Console.WriteLine(a.Speak()); // "woof"
```

Pitfalls:

- Avoid deep inheritance hierarchies; prefer composition and explicit interfaces.
- Virtual methods in constructors are dangerous (override called before derived constructor runs).

### Encapsulation & Access Modifiers

Modifiers: `public`, `internal`, `protected`, `private`, `protected internal`, `private protected`.

Rules:

- Expose behaviour (methods) not internal state (fields).
- Use properties with validation rather than public fields.

Example:

```csharp
public class BankAccount
{
    private decimal _balance;
    public decimal Balance => _balance;
    public void Deposit(decimal amt) { if (amt <= 0) throw new ArgumentException(); _balance += amt; }
}
```

### Design: SRP, DI, SOLID Summary

- SRP: single responsibility per class.
- Dependency Injection: prefer constructor injection, use `IServiceCollection` registration for ASP.NET or `HostBuilder` for generic hosts.
- SOLID quick tips:
  - S: Single Responsibility
  - O: Open/Closed (extend via interfaces)
  - L: Liskov Substitution (derived types must work where base is used)
  - I: Interface Segregation (small focused interfaces)
  - D: Dependency Inversion (depend on abstractions)

Example DI registration (ASP.NET Core):

```csharp
builder.Services.AddScoped<IUserService, UserService>();
```

---

## Modules, Namespaces & Assemblies

### Namespaces & `using`

- Namespaces organize types; use hierarchical names: `Company.Product.Module`.
- `using` imports namespaces; prefer file-scoped `using` declarations where appropriate (C# 10+):

```csharp
namespace MyApp.Features;

using System.Collections.Generic;
```

Notes:

- Avoid wildcard imports; prefer explicit naming to reduce ambiguity in large projects.

### Assemblies & `csproj`

- Assembly = compiled unit (DLL/EXE) with metadata.
- `*.csproj` is the project descriptor for SDK-style projects in modern .NET.

Minimal `csproj` example:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
  </ItemGroup>
</Project>
```

### NuGet and Versioning

- Publish libraries to NuGet for reuse. SemVer recommended: `Major.Minor.Patch`.
- Strong-name assemblies only when required for GAC or strict signing requirements.

---

## Coding Style & Conventions

This section aligns with .NET/C# community and Microsoft conventions and adds practical rules used in production.

### Naming, Indentation, Braces, XML docs

- **Naming**:
  - Types (classes, structs, enums, interfaces): `PascalCase` (e.g., `UserRepository`).
  - Interfaces: `PascalCase` with `I` prefix (e.g., `IRepository`).
  - Methods and Properties: `PascalCase`.
  - Local variables and parameters: `camelCase`.
  - Private fields: `_camelCase` (leading underscore) or `camelCase` depending on team style.
  - Constants: `PascalCase` (or `ALL_CAPS` rarely used in .NET).

- **Indentation**: 4 spaces (no tabs).
- **Brace style**: place opening brace on new line (Allman) for types and members — this is the Microsoft style. Example:

```csharp
public class Foo
{
    public void Bar()
    {
        // code
    }
}
```

- **XML documentation**: Use `/// <summary>` for public APIs and include param/returns tags.

```csharp
/// <summary>Gets the user by id.</summary>
/// <param name="id">User identifier.</param>
/// <returns>User object or null.</returns>
public User? GetUser(int id) { ... }
```

- **Comments**: Prefer meaningful code to comments. Use comments for rationale, not for restating code.

### Best practices for readability, maintainability & performance

- Keep methods short (ideally < 40 lines). Single responsibility per method.
- Prefer `async`/`await` for I/O-bound work and avoid `Task.Run` for CPU-bound operations in server code.
- Use `ConfigureAwait(false)` in library code (non-UI) where appropriate.
- Use `IEnumerable<T>`/`IReadOnlyCollection<T>` for read-only parameters to hide implementation details.
- Prefer `foreach` over `for` when readability wins; use indexes when you need them.
- Avoid `null` where possible; prefer `nullable reference types` feature (`string?`) and annotate APIs.
- Use `StringBuilder` for heavy string concatenation in loops. Use `string.Concat` or interpolation for light usage.
- Avoid exceptions for control flow — they are expensive.

Performance-specific:

- Use `Span<T>`/`Memory<T>` for zero-copy slices.
- Prefer `struct` for small value types; prefer `class` for entities and polymorphic behavior.
- Use `ArrayPool<T>` to reduce allocations in hot paths.

---

## Testing, Debugging & Tooling

- Unit testing: `xUnit`, `NUnit`, `MSTest`. Mocking: `Moq`, `NSubstitute`.
- Integration testing: use `WebApplicationFactory<TEntryPoint>` for ASP.NET Core integration tests.
- Code analysis: `dotnet format`, `Roslyn analyzers`, `FxCop`/`Microsoft.CodeAnalysis` rules.
- Profiling: Visual Studio Profiler, `dotnet-counters`, `dotnet-trace`, `perfcollect`.

Example test (xUnit):

```csharp
public class CalculatorTests
{
    [Fact]
    public void Add_ReturnsSum()
    {
        var calc = new Calculator();
        Assert.Equal(3, calc.Add(1,2));
    }
}
```

Debugging tips:

- Use conditional breakpoints and tracepoints to collect runtime info without stopping.
- Use `dotnet test --filter` to run subsets of tests.

---

## C# in the Modern .NET Ecosystem

- .NET is cross-platform and first-class on Windows, macOS, Linux. Use `dotnet` CLI for multi-platform builds.
- Use ASP.NET Core for web APIs, Blazor for client/web UIs, MAUI for native cross-platform GUI, and worker services for background processing.
- Modern .NET supports AOT, trimming, single-file publish for small deployment surfaces.

Interoperability:

- Use P/Invoke and `DllImport` to call native libraries.
- Use `System.Text.Json` for high-performance JSON; fallback to `Newtonsoft.Json` for advanced scenarios.

Deployment patterns:

- Containerize with `mcr.microsoft.com/dotnet/aspnet` or SDK images.
- Use CI/CD to build and publish NuGet artifacts and container images.

---

## Appendices — Cheatsheets & Common Patterns

### Common language idioms

- Null-safe access:

```csharp
var name = user?.Profile?.Name ?? "(unknown)";
```

- Pattern matching:

```csharp
if (o is Person p) Console.WriteLine(p.Name);
switch (shape) { case Circle c: ...; break; }
```

- `using` declaration (C#8+):

```csharp
using var conn = new SqlConnection(connStr);
```

### Common pitfalls checklist

- Forgetting `ConfigureAwait(false)` in library code (can cause deadlocks in certain sync contexts).
- Exposing mutable collections as public APIs; return `IReadOnlyCollection<T>` instead.
- Not implementing `IDisposable` correctly (use `SafeHandle` and `Dispose(bool)` pattern when necessary).

---

## References & Further Reading

- Microsoft docs: [C# Guide](https://learn.microsoft.com/dotnet/csharp/), [CLR overview](https://learn.microsoft.com/dotnet/standard/clr)
- .NET performance: [High-performance .NET](https://learn.microsoft.com/dotnet/standard/performance/)
- Effective C#: ["C# in Depth" by Jon Skeet] and ["Effective C#" by Bill Wagner]
- Roslyn and analyzers: [Roslyn GitHub](https://github.com/dotnet/roslyn)

---

_This guide follows the tone, structure, and style of other guides in this repository: header metadata, badges, an overview, contents list, thorough sections, code blocks, pitfalls, and practical recommendations._
