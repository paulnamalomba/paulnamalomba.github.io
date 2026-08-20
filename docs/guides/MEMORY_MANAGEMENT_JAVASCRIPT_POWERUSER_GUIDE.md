# Memory Management and Execution on Windows — JavaScript (Node.js)

**Last updated**: December 13, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>

- SESKA Computational Engineer<br>
- SEAT Backend Developer<br>
- Software Developer<br>
- PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Language: JavaScript](https://img.shields.io/badge/Language-JavaScript-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Runtime: Node.js](https://img.shields.io/badge/Runtime-Node.js-339933.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

This guide explains how JavaScript handles memory and execution semantics on Windows using the Node.js runtime (V8 engine). It covers value vs reference types, memory allocation (heap-managed objects), copy semantics (shallow vs deep), and nullability (`undefined`/`null`). Examples are provided for typical Node.js usage.

## Contents

- [Memory Management and Execution on Windows — JavaScript (Node.js)](#memory-management-and-execution-on-windows--javascript-nodejs)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Windows — Run (PowerShell / Command Prompt)](#windows--run-powershell--command-prompt)
  - [Overview](#overview-1)
  - [Contents](#contents-1)
  - [1) Data Structures — Primitive vs Object](#1-data-structures--primitive-vs-object)
  - [2) Storage — V8 Heap \& Stack](#2-storage--v8-heap--stack)
  - [3) Copy Semantics — Shallow vs Deep](#3-copy-semantics--shallow-vs-deep)
  - [4) Nullability — `undefined` vs `null`](#4-nullability--undefined-vs-null)
  - [Examples — Runnable Snippets](#examples--runnable-snippets)
  - [Windows / Node.js Specific Notes](#windows--nodejs-specific-notes)
  - [References](#references)

---

## Windows — Run (PowerShell / Command Prompt)

- Install Node.js and run `main.js`:

  ```powershell
  node main.js
  ```

- If using Deno or other runtimes, adjust commands accordingly.

---

## Overview

This guide explains how JavaScript (Node.js V8 engine) handles memory and execution semantics on Windows: value vs reference types, memory allocation (heap-managed objects), copy semantics (shallow vs deep), and nullability (`undefined`/`null`). Examples are provided for typical Node.js usage.

---

## Contents

- Data Structures: primitive vs object types
- Storage: V8 heap and stack, hidden classes, optimization
- Copy semantics: assignment, shallow vs deep copies
- Nullability: `undefined` vs `null`, safety patterns
- Examples & Best Practices
- Windows/Node.js specifics

---

## 1) Data Structures — Primitive vs Object

- Primitives: `number`, `string`, `boolean`, `null`, `undefined`, `symbol`, `bigint` — stored by value.
- Objects: `Object`, `Array`, `Function` — stored as references on the V8 heap.

Example:

```javascript
let a = 10;
let b = a; // value copy
b = 20; // a remains 10

let obj1 = { x: 1 };
let obj2 = obj1; // reference copy
obj2.x = 5; // obj1.x also 5
```

Notes:

- Strings are immutable; operations create new strings.

---

## 2) Storage — V8 Heap & Stack

- Primitive values may be stored on the stack or in registers for performance.
- Objects are allocated on the V8 heap, which is garbage-collected (Mark-and-Sweep, generational).
- V8 optimizes objects with hidden classes and inline caches to improve property access performance.

Windows/Node specifics:

- Node.js uses V8's memory management; adjust `--max-old-space-size` to change heap size.
- The event loop drives execution; asynchronous I/O operations do not block JS thread.

---

## 3) Copy Semantics — Shallow vs Deep

- Assignment: primitives copied by value; objects copied by reference.
- Shallow copy: `Object.assign({}, obj)` or spread `{...obj}` duplicates top-level properties. Nested objects still shared.
- Deep copy: structured cloning (`structuredClone`), `JSON.parse(JSON.stringify(obj))` (limitations), or utility libraries like `lodash.cloneDeep`.

Example:

```javascript
const orig = { a: { b: 1 } };
const shallow = { ...orig };
shallow.a.b = 2; // orig.a.b also 2

const deep = structuredClone(orig);
deep.a.b = 3; // orig unchanged
```

Pitfalls:

- `JSON`-based cloning loses functions, `undefined`, and special types (Date, Map, Set).

---

## 4) Nullability — `undefined` vs `null`

- `undefined` indicates missing value (variable declared but not assigned). `null` is an explicit assignment meaning "no value".
- Use optional chaining (`?.`) and nullish coalescing (`??`) to guard against `undefined`/`null`.

Example:

```javascript
let x;
console.log(x === undefined); // true
x = null;
console.log(x === null); // true

const name = user?.profile?.name ?? "anonymous";
```

Best practices:

- Prefer `undefined` for absent values internally and `null` for intentionally empty API responses, or pick a consistent convention in your codebase.

---

## Examples — Runnable Snippets

`main.js`:

```javascript
// primitives vs objects
let n = 1;
let m = n;
m = 2;
console.log(n, m); // 1 2

let o1 = { v: 1 };
let o2 = o1;
o2.v = 9;
console.log(o1.v); // 9

// shallow vs deep
const a = { x: { y: 1 } };
const shallow = { ...a };
shallow.x.y = 5;
console.log(a.x.y); // 5

const deep = structuredClone(a);
deep.x.y = 7;
console.log(a.x.y); // still 5

// nullish
let maybe;
console.log(maybe ?? "default");
```

Run with `node main.js`.

---

## Windows / Node.js Specific Notes

- Increase memory: `node --max-old-space-size=4096 main.js` (MB) for large data workloads.
- Use `--trace-gc` and `--inspect` for GC and profiler diagnostics.
- Native modules: `node-gyp` builds native addons; watch memory and lifecycle in native code.

---

## References

- V8 blog and docs: https://v8.dev/
- Node.js docs: https://nodejs.org/

_End of JavaScript guide._
