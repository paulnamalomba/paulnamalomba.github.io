# Memory-Aware Batching, Threading & MPI Chunking for Large Database Operations

<br>
**Last updated**: February 16, 2026<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>
[![Language: Python](https://img.shields.io/badge/Language-Python-3776AB.svg)](https://www.python.org/)
<!-- [![Language: C++](https://img.shields.io/badge/Language-C%2B%2B-blue.svg)](https://learn.microsoft.com/cpp) -->
[![HPC: MPI](https://img.shields.io/badge/HPC-MPI-orange.svg)](https://www.mpi-forum.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)
<br>
*C++ will come in a future update. For now, the Python implementation demonstrates the core algorithm effectively.*

## Context

We innovated this idea at database-level for our platform (SEAT) backend. That platform is written in Python with the Django framework, and uses PostgreSQL as the database engine. We had to perform bulk updates on tables with millions of rows, and found that naive/server-native/pessimistic approaches either exhausted RAM, underutilised the CPU, or saturated server disk I/O leading to quite frankly, insane performance inefficiencies that trickle down into affecting platform availability and uptime. This guide distills our solution into a general-purpose algorithm that can be applied in any language or database context. With examples given in both Python and C++, and a detailed numerical breakdown of how the algorithm adapts to different RAM profiles and data sizes, this guide is a practical resource for developers facing similar challenges with large database operations. The three-stage pipeline we present — _Memory-Aware Batching → Thread-Level Buffering → MPI Core-Level Chunking_ — is designed to dynamically adapt to available system resources, ensuring efficient processing without overwhelming the server.

## Foundational Assumptions

The algorithm presented here is a self-tuning algorithm with respect to the host machine characteristics: it reads total **available physical RAM**, reserves a **10% safety overhead**, **partitions the remaining budget into lightweight thread buffers**, and then **distributes each buffer's workload across logical cores via MPI scatter/gather**. We assume disk I/O throughput is that of a PCIe Gen 4 NVMe at ~5.5 GB/s maximum. This is factored into the algorithm so that neither the storage subsystem nor the memory subsystem becomes the bottleneck.

Two real-world scenarios are analysed in detail:

| Scenario                | Total data | Row size | Row count      |
| ----------------------- | ---------- | -------- | -------------- |
| **A** — Heavy update    | 10 GB      | 5 KB     | 2 097 152 rows |
| **B** — Moderate update | 3 GB       | 20 KB    | 157 286 rows   |

Each scenario is evaluated against three theoretical RAM profiles: **24 GB**, **8 GB**, and **4 GB**.

## Contents

- [Memory-Aware Batching, Threading \& MPI Chunking for Large Database Operations](#memory-aware-batching-threading--mpi-chunking-for-large-database-operations)
  - [Context](#context)
  - [Foundational Assumptions](#foundational-assumptions)
  - [Contents](#contents)
  - [1) Problem Statement \& Hardware Model](#1-problem-statement--hardware-model)
  - [2) The Three-Stage Pipeline](#2-the-three-stage-pipeline)
  - [3) Stage 1 — Memory-Aware Batch Sizing Algorithm](#3-stage-1--memory-aware-batch-sizing-algorithm)
  - [4) Stage 2 — Thread-Level Buffer Partitioning](#4-stage-2--thread-level-buffer-partitioning)
  - [5) Stage 3 — MPI Core-Level Chunking](#5-stage-3--mpi-core-level-chunking)
  - [6) Disk I/O Constraint — NVMe Throughput Gate](#6-disk-io-constraint--nvme-throughput-gate)
  - [7) Worked Scenarios — Numerical Breakdown](#7-worked-scenarios--numerical-breakdown)
    - [Scenario A — Heavy Update (10 GB / 5 KB rows → 2 097 152 rows)](#scenario-a--heavy-update-10-gb--5-kb-rows--2-097-152-rows)
    - [Scenario B — Moderate Update (3 GB / 20 KB rows → 157 286 rows)](#scenario-b--moderate-update-3-gb--20-kb-rows--157-286-rows)
    - [Discussion — Why Does Total I/O Time Converge Across All RAM Sizes?](#discussion--why-does-total-io-time-converge-across-all-ram-sizes)
  - [8) Python Reference Implementation](#8-python-reference-implementation)
  - [9) Performance Notes \& Pitfalls](#9-performance-notes--pitfalls)
  - [References](#references)

---

## 1) Problem Statement & Hardware Model

You have a database with `N` rows, each of size `R` bytes, requiring a bulk update of total size `D = N × R`. The machine has:

| Parameter                         | Symbol      | Typical values                     |
| --------------------------------- | ----------- | ---------------------------------- |
| Total physical RAM                | `RAM_total` | 4 GB / 8 GB / 24 GB                |
| OS + base process overhead        | `RAM_os`    | ~1.5 GB (Windows), ~0.8 GB (Linux) |
| Safety overhead (always reserved) | `α`         | 10 % of `RAM_total`                |
| Logical CPU cores                 | `C`         | 4 / 8 / 16                         |
| Disk sequential read/write        | `IO_max`    | ~5.5 GB/s (PCIe Gen 4 NVMe SSD)    |
| Disk queue depth (NVMe)           | `QD`        | 32–64                              |

The **usable budget** or in other words **maximum expendable data-effort** for the batcher is:

```
RAM_usable = RAM_total − RAM_os − (α × RAM_total)
```

This is the ceiling the algorithm must never exceed.

---

## 2) The Three-Stage Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA SOURCE  (D bytes)                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                 ┌──────────────▼──────────────┐
                 │      STAGE 1: BATCHER       │   ← RAM-aware
                 │    Splits D into N_batch    │     batch_size ≤ RAM_usable
                 │     sequential batches      │
                 └──────────────┬──────────────┘
                                │  one batch at a time
                    ┌───────────▼───────────┐
                    │   STAGE 2: THREADER   │   ← buffer partitioning
                    │   Splits batch into   │     T lightweight threads
                    │  thread_buf = batch/T │
                    └───────────┬───────────┘
                                │  T concurrent buffers (lightweight threads)
              ┌─────────────────┼─────────────────┐
              │                 │                 │
    ┌─────────▼──────┐ ┌───────▼────────┐ ┌──────▼─────────┐
    │  STAGE 3: MPI  │ │  STAGE 3: MPI  │ │  STAGE 3: MPI  │
    │  chunk = buf/C │ │  chunk = buf/C │ │  chunk = buf/C │
    │  → core 0..C-1 │ │  → core 1..C-1 │ │  → core 2..C-1 │
    └────────────────┘ └────────────────┘ └────────────────┘
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   COMMIT / WRITE-BACK │   ← disk I/O gated
                    └───────────────────────┘
```

Each stage enforces a different resource constraint:

| Stage       | Governs          | Constraint                       |
| ----------- | ---------------- | -------------------------------- |
| Batcher     | RAM ceiling      | `batch_size ≤ RAM_usable`        |
| Threader    | Concurrency      | `thread_buffer = batch_size / T` |
| MPI Chunker | Core utilisation | `chunk = thread_buffer / C`      |

---

## 3) Stage 1 — Memory-Aware Batch Sizing Algorithm

The batcher answers one question: _how many rows can I hold in RAM at once without exceeding the usable budget?_

**Algorithm:**

```
INPUT:  RAM_total, RAM_os, α, row_size, total_rows
OUTPUT: batch_size (bytes), rows_per_batch, num_batches

1.  RAM_usable  = RAM_total − RAM_os − (α × RAM_total)
2.  batch_size  = RAM_usable                            # fill the budget
3.  rows_per_batch = floor(batch_size / row_size)
4.  num_batches    = ceil(total_rows / rows_per_batch)
5.  RETURN batch_size, rows_per_batch, num_batches
```

The batch size dynamically adapts: on a 24 GB machine you get large batches (few iterations), on a 4 GB machine you get small batches (many iterations). The total work is identical; only the iteration count changes.

Notes:

- `RAM_os` should be measured, not assumed. On Windows, use `GlobalMemoryStatusEx`; on Linux, read `/proc/meminfo`. In Python, `psutil.virtual_memory()` provides this portably.
- The 10 % overhead (`α = 0.10`) absorbs transient allocations: serialisation buffers, ORM object headers, GC pressure spikes.

---

## 4) Stage 2 — Thread-Level Buffer Partitioning

Once a batch is loaded into RAM, it is subdivided into `T` independent thread buffers. Each thread operates on a non-overlapping slice of the batch.

**Algorithm:**

```
INPUT:  batch_size, T (num threads)
OUTPUT: thread_buffer_size, rows_per_thread

1.  thread_buffer_size = floor(batch_size / T)
2.  rows_per_thread    = floor(thread_buffer_size / row_size)
3.  remainder_rows     = rows_per_batch − (T × rows_per_thread)
4.  Assign remainder_rows to the last thread (or distribute round-robin)
5.  RETURN thread_buffer_size, rows_per_thread
```

T must either be chosen based on your target buffer size (`thread_buffer_size`) of scaled by number of logical cores or simply an arbitrary number as per your choice. How to choose `T`:

- `T` should not exceed the logical core count `C`; going beyond causes context-switch overhead.
- For I/O-bound workloads (database writes), `T = 2 × C` can be acceptable because threads spend time waiting on I/O.
- For CPU-bound transforms, `T = C` is optimal.

A better way would be to choose `thread_buffer_size` first (e.g. 50 MB), then derive `T = floor(batch_size / thread_buffer_size)`, capping at `C`.

Notes:

- In `Python`, the GIL prevents true parallel CPU execution across threads. Use `multiprocessing` or `concurrent.futures.ProcessPoolExecutor` for CPU-bound work. For I/O-bound database calls, `threading` / `ThreadPoolExecutor` is effective because the GIL is released during I/O waits.
- In `C++`, `std::thread` or OpenMP libraries give true shared-memory parallelism without a GIL.
- GIL: Global Interpreter Lock disallows more than 1 thread to control the process [read more @ https://realpython.com/python-gil/](https://realpython.com/python-gil).

---

## 5) Stage 3 — MPI Core-Level Chunking

Each thread buffer is further decomposed into `C` chunks, one per logical core, distributed via MPI `Scatter` / `Gather` (or in a shared-memory context, via OpenMP work-sharing).

**Algorithm:**

```
INPUT:  thread_buffer_size, C (logical cores)
OUTPUT: chunk_size, rows_per_chunk

1.  chunk_size     = floor(thread_buffer_size / C)
2.  rows_per_chunk = floor(chunk_size / row_size)
3.  MPI_Scatter(thread_buffer, chunk_size, root=0)
4.  Each rank processes its chunk independently
5.  MPI_Gather(results, root=0)
6.  RETURN aggregated results
```

Example — if `thread_buffer_size = 50 MB` and `C = 10`:

```
chunk_size = 50 MB / 10 = 5 MB per core
```

**All 10 cores execute concurrently. Wall-clock time for this thread's work drops to ≈ 1/10th of sequential.**

Notes:

- MPI ranks can span multiple nodes (distributed memory) or be confined to a single node (shared memory). For database batching on a single server, `MPI_COMM_WORLD` maps to local cores.
- Prefer `MPI_Scatterv` / `MPI_Gatherv` when chunk sizes are uneven (remainder rows).
- In Python, `mpi4py` provides full MPI bindings. In C++, use the native MPI C API or Boost.MPI.

---

## 6) Disk I/O Constraint — NVMe Throughput Gate

Even with unlimited RAM and cores, the disk is the final bottleneck. A PCIe Gen 4 NVMe SSD delivers:

| Metric                 | Value                  |
| ---------------------- | ---------------------- |
| Sequential read        | ~5.5 GB/s              |
| Sequential write       | ~5.0 GB/s              |
| Random 4K read (QD32)  | ~700K IOPS → ~2.7 GB/s |
| Random 4K write (QD32) | ~500K IOPS → ~1.9 GB/s |

Database writes are typically **random** (updating rows at arbitrary offsets), so effective throughput may drop to ~1.5–2.5 GB/s depending on the database engine and WAL configuration.

**I/O gate rule:** the batcher should not produce batches faster than the disk can absorb them. If `batch_size / IO_effective > batch_compute_time`, insert a throttle:

```
IO_time_estimate = batch_size / IO_effective
if compute_time < IO_time_estimate:
    sleep(IO_time_estimate − compute_time)   # or use backpressure
```

In practice, the database engine's write-ahead log (WAL) and `fsync` latency naturally throttle throughput. The batcher simply needs to avoid queuing dozens of batches in memory while the disk is still flushing earlier ones — hence the single-batch-at-a-time design in Stage 1.

---

## 7) Worked Scenarios — Numerical Breakdown

Assumptions for all scenarios:

- `RAM_os` = 1.5 GB (Windows with typical services)
- `α` = 0.10 (10 % safety overhead)
- `C` = 8 logical cores
- `T` = 8 threads (1 thread per core, CPU-bound model)
- `thread_buffer_size` = 50 MB

### Scenario A — Heavy Update (10 GB / 5 KB rows → 2 097 152 rows)

| Machine   | RAM_total | RAM_usable                   | batch_size           | rows/batch      | num_batches | thread_buf | chunk/core |
| --------- | --------- | ---------------------------- | -------------------- | --------------- | ----------- | ---------- | ---------- |
| **24 GB** | 24 GB     | 24 − 1.5 − 2.4 = **20.1 GB** | 10 GB (data fits ×2) | 2 097 152 (all) | **1**       | 1.25 GB    | 160 MB     |
| **8 GB**  | 8 GB      | 8 − 1.5 − 0.8 = **5.7 GB**   | 5.7 GB               | 1 196 236       | **2**       | 731 MB     | 91.4 MB    |
| **4 GB**  | 4 GB      | 4 − 1.5 − 0.4 = **2.1 GB**   | 2.1 GB               | 440 401         | **5**       | 268 MB     | 33.6 MB    |

Observations (Different Buffer Sizes & Iteration Counts):

- The 24 GB machine loads the entire 10 GB dataset in a single batch with ~10 GB headroom remaining. No iteration needed.
- The 8 GB machine runs 2 batches. Each batch fills ~5.7 GB, processes it across 8 cores, commits, then loads the next.
- The 4 GB machine runs 5 batches of ~2.1 GB each. More iterations but each is fully parallelised.

I/O check (worst case, random writes at ~2 GB/s):

- 24 GB: 10 GB / 2 GB/s = **5.0 s** wall-clock per **write function call**.
- 8 GB: 5.7 GB / 2 GB/s = **2.85 s** per batch × 2 = **5.7 s** total per **write function call**.
- 4 GB: 2.1 GB / 2 GB/s = **1.05 s** per batch × 5 = **5.25 s** total per **write function call**.

All converge to roughly the same total I/O time — the disk is the equaliser.

Observations (Same Buffer Sizes):

- The 24 GB machine loads the entire 10 GB dataset in 25 batches (`8 x 50 MB = 400 MB` each) with ~10 GB headroom remaining. No iteration needed.
- The 8 GB machine runs 25 batches (`8 x 50 MB = 400 MB` each). but can only load 14 batches at a time. Means 1 iterations of 14 batches then another of 11 batches.
- The 4 GB machine runs 25 batches (`8 x 50 MB = 400 MB` each), but can only load 5 batches at a time. Means 5 iterations of 5 batches each.

I/O check (worst case, random writes at ~2 GB/s):

- 24 GB: 10 GB / 2 GB/s = **5.0 s** wall-clock per **write function call**.
- 8 GB: 5.7 GB / 2 GB/s = **2.85 s** per batch × 2 = **5.7 s** total per **write function call**.
- 4 GB: 2.1 GB / 2 GB/s = **1.05 s** per batch × 5 = **5.25 s** total per **write function call**.

All converge to roughly the same total I/O time — the disk is the equaliser.

### Scenario B — Moderate Update (3 GB / 20 KB rows → 157 286 rows)

| Machine   | RAM_total | RAM_usable | batch_size | rows/batch    | num_batches | thread_buf | chunk/core |
| --------- | --------- | ---------- | ---------- | ------------- | ----------- | ---------- | ---------- |
| **24 GB** | 24 GB     | 20.1 GB    | 3 GB (all) | 157 286 (all) | **1**       | 384 MB     | 48 MB      |
| **8 GB**  | 8 GB      | 5.7 GB     | 3 GB (all) | 157 286 (all) | **1**       | 384 MB     | 48 MB      |
| **4 GB**  | 4 GB      | 2.1 GB     | 2.1 GB     | 110 100       | **2**       | 268 MB     | 33.6 MB    |

Observations:

- Both the 24 GB and 8 GB machines fit the entire 3 GB payload in one batch.
- Only the 4 GB machine needs 2 batches.
- Larger row sizes (20 KB) mean fewer rows and lower ORM overhead per row.

### Discussion — Why Does Total I/O Time Converge Across All RAM Sizes?

This is the most important insight in the entire guide. Notice that whether we use 24 GB, 8 GB, or 4 GB of RAM — and whether we use variable or fixed buffer sizes — the total wall-clock time for disk writes always lands at roughly **5 seconds** for Scenario A. This is not a coincidence. It is a mathematical inevitability. So you do not have to have a MEGA RAM machine to achieve good performance on large database operations. The algorithm adapts to the RAM you have, and the disk I/O time converges to the same value, based on smart batching and parallelism. The key would actually be a faster SSD and faster RAM, perhaps faster PostgreSQL configuration such as dedicated RAM pool (e.g. WAL settings, checkpoint intervals) to reduce the I/O bottleneck.

**The total bytes written to disk is constant.** The disk does not care how you partition the work in RAM. It receives the same 10 GB of row updates regardless of batching strategy:

```
 24 GB machine:   1 batch  × 10.0 GB  =  10 GB hits the disk
  8 GB machine:   2 batches ×  5.7 GB ≈  10 GB hits the disk
  4 GB machine:   5 batches ×  2.1 GB ≈  10 GB hits the disk
```

The disk writes at ~2 GB/s (random 4K writes on NVMe). Therefore:

```
Total I/O time  =  Total data  ÷  Disk throughput
                =  10 GB       ÷  2 GB/s
                ≈  5.0 s          (always)
```

This holds no matter how you slice the data. Think of it as a funnel:

```
        ┌──────────────────────┐
        │    RAM (wide top)    │   ← batching: variable, adapts to machine
        │  ████████████████    │
        └──────────┬───────────┘
                   │
           ┌───────▼───────┐
           │  CPU / Cores  │       ← threading + MPI: fast, parallel
           │  ████████████ │
           └───────┬───────┘
                   │
              ┌────▼────┐
              │  DISK   │          ← fixed throughput: ~2 GB/s
              │  █████  │            this is the narrow spout
              └─────────┘
```

RAM and cores control how fast you _prepare_ data (compute phase: ORM serialisation, row transforms, query construction). But for database bulk writes, compute cost is microseconds-per-row while disk I/O is the dominant wall-clock cost by orders of magnitude. The compute phase is effectively instantaneous relative to the I/O phase.

**Where more RAM does provide a measurable (but small) advantage:**

| Benefit                              | Mechanism                                                                 | Magnitude                   |
| ------------------------------------ | ------------------------------------------------------------------------- | --------------------------- |
| Fewer `COMMIT` / `fsync` round-trips | Each transaction commit forces a WAL flush; fewer batches = fewer flushes | ~0.1–5 ms per commit        |
| Less orchestration overhead          | Fewer batch loop iterations, fewer `ProcessPoolExecutor` startups         | ~10–50 ms per batch         |
| Better CPU cache locality            | One large contiguous buffer vs many small ones reduces L2/L3 cache misses | Marginal for I/O-bound work |
| Reduced context switching            | Fewer batch transitions = fewer OS scheduler interruptions                | ~1–10 ms per switch         |

These savings total perhaps **50–200 ms** across the entire 10 GB operation — negligible against **5 000 ms** of disk I/O. The disk is the equaliser.

**When does more RAM actually matter?** When the _compute_ phase is expensive relative to I/O — for example, if each row requires a heavy cryptographic hash, a machine learning inference, or a complex geometric transform before writing. In that case, larger batches mean fewer re-initialisations of the compute pipeline, and the CPU (not the disk) becomes the bottleneck. For straightforward database `UPDATE` / `INSERT` operations, the disk dominates.

**Scaling context — per-process view:** The numbers above are for a single process (i.e. one function call writing row-level data in bulk to the database). In a real system with a module that performs hundreds of Django `filter → update → save` operations, each call independently hits this same I/O floor. If you have 100 such calls each writing 10 GB, the total time is ~100 × 5 s = **500 s** (~8.3 minutes), regardless of RAM. The only way to reduce this is to upgrade the disk (PCIe Gen 5, RAID-0 striping) or reduce the total data volume.

---

## 8) Python Reference Implementation

A minimal, platform-agnostic implementation demonstrating the three-stage algorithm. Uses `psutil` for RAM detection and `multiprocessing` for core-level parallelism (substituting for MPI in single-node deployments).

```python
"""
memory_aware_batcher.py
Demonstrates the Memory-Aware Batcher algorithm.
"""

import math
import os
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import List, Tuple

try:
    import psutil
except ImportError:
    psutil = None


#  Stage 1 — Memory-Aware Batch Sizing
# ──────────────────────────────────────────────
def compute_batch_params(
    total_data_bytes: int,
    row_size_bytes: int,
    ram_total: int = None,
    ram_os: int = 1_500_000_000,       # 1.5 GB default
    overhead_fraction: float = 0.10,
) -> Tuple[int, int, int]:
    """
    Returns (batch_size_bytes, rows_per_batch, num_batches).
    Dynamically sizes batches to fit within usable RAM.
    """
    if ram_total is None:
        if psutil:
            ram_total = psutil.virtual_memory().total
        else:
            raise RuntimeError("psutil not available; pass ram_total explicitly")

    ram_usable = ram_total - ram_os - int(overhead_fraction * ram_total)
    if ram_usable <= 0:
        raise MemoryError(f"Usable RAM is non-positive: {ram_usable}")

    # Batch size is the smaller of usable RAM and total data
    batch_size = min(ram_usable, total_data_bytes)
    rows_per_batch = batch_size // row_size_bytes
    if rows_per_batch == 0:
        raise MemoryError("Row size exceeds usable RAM")

    total_rows = total_data_bytes // row_size_bytes
    num_batches = math.ceil(total_rows / rows_per_batch)

    return batch_size, rows_per_batch, num_batches


#  Stage 2 — Thread-Level Buffer Partitioning
# ──────────────────────────────────────────────
def partition_into_threads(
    rows_per_batch: int,
    num_threads: int = None,
) -> List[Tuple[int, int]]:
    """
    Splits rows_per_batch into non-overlapping slices.
    Returns list of (start_row, end_row) tuples.
    """
    if num_threads is None:
        num_threads = os.cpu_count() or 4

    base = rows_per_batch // num_threads
    remainder = rows_per_batch % num_threads
    slices = []
    offset = 0
    for i in range(num_threads):
        count = base + (1 if i < remainder else 0)
        slices.append((offset, offset + count))
        offset += count
    return slices

#  Stage 3 — Core-Level Chunking (MPI-style)
# ──────────────────────────────────────────────
def _process_chunk(args: Tuple[int, int, int]) -> int:
    """
    Worker function executed on a single core.
    Receives (chunk_start, chunk_end, batch_id).
    Returns number of rows processed (placeholder).
    """
    chunk_start, chunk_end, batch_id = args
    rows_processed = chunk_end - chunk_start
    # ── replace with actual DB update logic ──
    #   e.g. UPDATE table SET ... WHERE id BETWEEN chunk_start AND chunk_end
    return rows_processed


def scatter_to_cores(
    thread_start: int,
    thread_end: int,
    batch_id: int,
    num_cores: int = None,
) -> int:
    """
    Distributes a thread-buffer's row range across logical cores
    using multiprocessing (single-node MPI equivalent).
    """
    if num_cores is None:
        num_cores = os.cpu_count() or 4

    total_rows = thread_end - thread_start
    base = total_rows // num_cores
    remainder = total_rows % num_cores

    chunks = []
    offset = thread_start
    for i in range(num_cores):
        count = base + (1 if i < remainder else 0)
        chunks.append((offset, offset + count, batch_id))
        offset += count

    with ProcessPoolExecutor(max_workers=num_cores) as pool:
        results = list(pool.map(_process_chunk, chunks))

    return sum(results)

#  Orchestrator
# ──────────────────────────────────────────────
def run_batcher(
    total_data_bytes: int,
    row_size_bytes: int,
    ram_total: int = None,
):
    batch_size, rows_per_batch, num_batches = compute_batch_params(
        total_data_bytes, row_size_bytes, ram_total=ram_total,
    )
    total_rows = total_data_bytes // row_size_bytes
    num_threads = os.cpu_count() or 4
    num_cores = num_threads  # 1:1 thread-to-core mapping

    print(f"{'='*60}")
    print(f"  RAM total       : {(ram_total or 0) / 1e9:.1f} GB")
    print(f"  Batch size      : {batch_size / 1e9:.2f} GB")
    print(f"  Rows per batch  : {rows_per_batch:,}")
    print(f"  Num batches     : {num_batches}")
    print(f"  Threads         : {num_threads}")
    print(f"  Cores per thread: {num_cores}")
    print(f"{'='*60}")

    processed = 0
    for batch_id in range(num_batches):
        batch_start = batch_id * rows_per_batch
        batch_end = min(batch_start + rows_per_batch, total_rows)
        current_batch_rows = batch_end - batch_start

        # Stage 2 — partition into thread buffers
        slices = partition_into_threads(current_batch_rows, num_threads)

        # Stage 3 — scatter each thread buffer across cores
        for (t_start, t_end) in slices:
            absolute_start = batch_start + t_start
            absolute_end = batch_start + t_end
            processed += scatter_to_cores(
                absolute_start, absolute_end, batch_id, num_cores,
            )

        print(f"  Batch {batch_id + 1}/{num_batches} committed "
              f"({current_batch_rows:,} rows)")

    print(f"\n  Total rows processed: {processed:,}")

#  Entry point — run all scenarios
# ──────────────────────────────────────────────
if __name__ == "__main__":
    GB = 1_073_741_824  # 1 GiB in bytes
    KB = 1_024

    scenarios = [
        ("A: 10 GB / 5 KB rows", 10 * GB, 5 * KB),
        ("B: 3 GB / 20 KB rows", 3 * GB, 20 * KB),
    ]
    ram_profiles = [24 * GB, 8 * GB, 4 * GB]

    for label, data, row in scenarios:
        for ram in ram_profiles:
            print(f"\n>>> Scenario {label} | RAM = {ram // GB} GB")
            run_batcher(data, row, ram_total=ram)
```

Run:

```powershell
python memory_aware_batcher.py
```

Notes:

- `ProcessPoolExecutor` sidesteps the GIL for CPU-bound chunk processing.
- For true MPI across nodes, replace `ProcessPoolExecutor` with `mpi4py.MPI.COMM_WORLD.Scatter` / `Gather`.
- The `_process_chunk` worker is the integration point — plug in your ORM / raw SQL update logic there.

<!-- ---

## 9) C++ Reference Implementation

A minimal C++ implementation using MPI for core-level distribution. Compile with an MPI-aware compiler (`mpicxx`).

```cpp
/*
 * memory_aware_batcher.cpp
 * Demonstrates the three-stage Memory-Aware Batcher with MPI.
 *
 * Compile:  mpicxx -O2 -o batcher memory_aware_batcher.cpp
 * Run:      mpirun -np 8 ./batcher
 */

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>
#include <mpi.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

// ── Platform-specific RAM detection ──
static int64_t get_total_ram() {
#ifdef _WIN32
    MEMORYSTATUSEX ms;
    ms.dwLength = sizeof(ms);
    GlobalMemoryStatusEx(&ms);
    return static_cast<int64_t>(ms.ullTotalPhys);
#else
    long pages = sysconf(_SC_PHYS_PAGES);
    long page_size = sysconf(_SC_PAGE_SIZE);
    return static_cast<int64_t>(pages) * page_size;
#endif
}

// ── Stage 1: Batch sizing ──
struct BatchParams {
    int64_t batch_size;
    int64_t rows_per_batch;
    int64_t num_batches;
};

BatchParams compute_batch_params(
    int64_t total_data, int64_t row_size,
    int64_t ram_total, int64_t ram_os = 1'500'000'000,
    double alpha = 0.10)
{
    int64_t ram_usable = ram_total - ram_os
                       - static_cast<int64_t>(alpha * ram_total);
    int64_t batch_size = std::min(ram_usable, total_data);
    int64_t rows_per_batch = batch_size / row_size;
    int64_t total_rows = total_data / row_size;
    int64_t num_batches = (total_rows + rows_per_batch - 1) / rows_per_batch;
    return {batch_size, rows_per_batch, num_batches};
}

// ── Stage 3 worker: process a chunk ──
int64_t process_chunk(int64_t start, int64_t end) {
    // Replace with actual DB update logic
    return end - start;
}

// ── Main ──
int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank, world_size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    constexpr int64_t GB = 1'073'741'824LL;
    constexpr int64_t KB = 1'024LL;

    int64_t total_data = 10 * GB;
    int64_t row_size   = 5 * KB;
    int64_t ram_total  = get_total_ram();

    auto bp = compute_batch_params(total_data, row_size, ram_total);
    int64_t total_rows = total_data / row_size;

    if (rank == 0) {
        std::printf("RAM: %.1f GB | batch: %.2f GB | "
                    "rows/batch: %lld | batches: %lld | ranks: %d\n",
                    ram_total / 1e9, bp.batch_size / 1e9,
                    bp.rows_per_batch, bp.num_batches, world_size);
    }

    for (int64_t b = 0; b < bp.num_batches; ++b) {
        int64_t batch_start = b * bp.rows_per_batch;
        int64_t batch_end   = std::min(batch_start + bp.rows_per_batch,
                                       total_rows);
        int64_t batch_rows  = batch_end - batch_start;

        // Stage 2+3: distribute rows across MPI ranks
        int64_t base  = batch_rows / world_size;
        int64_t extra = batch_rows % world_size;
        int64_t my_count = base + (rank < extra ? 1 : 0);
        int64_t my_start = batch_start;
        for (int r = 0; r < rank; ++r)
            my_start += base + (r < extra ? 1 : 0);

        int64_t local_result = process_chunk(my_start,
                                             my_start + my_count);

        int64_t global_result = 0;
        MPI_Reduce(&local_result, &global_result, 1,
                   MPI_INT64_T, MPI_SUM, 0, MPI_COMM_WORLD);

        if (rank == 0) {
            std::printf("  Batch %lld/%lld done — %lld rows\n",
                        b + 1, bp.num_batches, global_result);
        }
    }

    MPI_Finalize();
    return 0;
}
``` -->

<!-- Compile & run:

```powershell
# Linux / WSL
mpicxx -O2 -o batcher memory_aware_batcher.cpp
mpirun -np 8 ./batcher

# Windows with MS-MPI
cl /EHsc /O2 memory_aware_batcher.cpp /I"%MSMPI_INC%" /link msmpi.lib
mpiexec -n 8 batcher.exe
```

Notes:
- `MPI_Reduce` with `MPI_SUM` aggregates per-rank results back to rank 0.
- For uneven distributions, `MPI_Scatterv` / `MPI_Gatherv` with per-rank displacement arrays is preferred.
- The `process_chunk` function is the integration point — plug in your database driver calls there. -->

---

## 9) Performance Notes & Pitfalls

**RAM management:**

- Always measure, never assume. `import psutil; psutil.virtual_memory()` (Python) give live values.
- The 10 % overhead (`α`) is a conservative default. In garbage-in-garbage-out style runtimes like Python, consider 25–30 %.
- Monitor RSS (Resident Set Size) at runtime. If it approaches `RAM_usable`, reduce `batch_size` dynamically.

**Threading:**

- CPython's GIL prevents parallel CPU-bound threads. Use `multiprocessing` or `ProcessPoolExecutor`.

<!-- - In C++, `std::thread` or OpenMP provide true parallelism. Avoid false sharing on cache lines (64-byte alignment). -->

- Thread count beyond core count is only beneficial for I/O-bound workloads.

**MPI considerations:**

- `MPI_Init` / `MPI_Finalize` must bracket all MPI calls.
- Prefer non-blocking collectives (`MPI_Iscatter`, `MPI_Igather`) for overlapping computation and communication.
- On a single node, MPI over shared memory (`--mca btl sm,self` in OpenMPI) avoids network stack overhead.

**Disk I/O:**

- NVMe sequential throughput (5.5 GB/s) applies only to large contiguous reads/writes. Database row updates are random-access.
- Effective random write throughput on NVMe is typically 1.5–2.5 GB/s depending on block size and queue depth.
- Batch commits should align with database page sizes (typically 8 KB for PostgreSQL, 16 KB for InnoDB) to minimise write amplification.
- Disk WAL (Write-Ahead Log) flushes are the true bottleneck for transactional databases. Tuning `wal_buffers` (PostgreSQL) or `innodb_log_buffer_size` (MySQL) can help --- logs are huge-space eaters, to keep it stupid and simple.

**Database-specific tips:**

- Use `COPY` (PostgreSQL) or `LOAD DATA INFILE` (MySQL) for bulk inserts — orders of magnitude faster than row-by-row `INSERT`.
- Wrap each batch in a single transaction. Committing per-row is catastrophically slow.
- Disable indexes and constraints during bulk loads, rebuild afterwards.
- Use `UNLOGGED` tables (PostgreSQL) for intermediate staging if crash-safety is not required during the load.

---

## References

- MPI Forum specification: [https://www.mpi-forum.org/docs/](https://www.mpi-forum.org/docs/)
- mpi4py documentation: [https://mpi4py.readthedocs.io/](https://mpi4py.readthedocs.io/)
- Python `multiprocessing` module: [https://docs.python.org/3/library/multiprocessing.html](https://docs.python.org/3/library/multiprocessing.html)
- NVMe specification (NVM Express): [https://nvmexpress.org/specifications/](https://nvmexpress.org/specifications/)
- PostgreSQL bulk loading: [https://www.postgresql.org/docs/current/populate.html](https://www.postgresql.org/docs/current/populate.html)
- psutil — cross-platform system monitoring: [https://psutil.readthedocs.io/](https://psutil.readthedocs.io/)
- Python GIL explained: [https://realpython.com/python-gil/](https://realpython.com/python-gil/)
