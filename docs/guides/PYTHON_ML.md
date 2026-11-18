# Python for machine learning: engineering the AI pipeline

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
[![Language](https://img.shields.io/badge/Language-Python_3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

Python exposes optimized C/C++ libraries through APIs suited to machine learning work. This guide covers constructing, vectorizing, and deploying AI pipelines with NumPy, Pandas, Scikit-Learn, and PyTorch.

## Contents

- [Python for machine learning: engineering the AI pipeline](#python-for-machine-learning-engineering-the-ai-pipeline)
  - [Overview](#overview)
  - [Contents](#contents)
  - [1. Configuration (Windows \& Linux)](#1-configuration-windows--linux)
    - [Dependency \& environment management](#dependency--environment-management)
    - [Windows PATH and GPU drivers](#windows-path-and-gpu-drivers)
  - [2. Writing basic Code/scripts (core ML frameworks)](#2-writing-basic-codescripts-core-ml-frameworks)
    - [Data manipulation: NumPy \& Pandas](#data-manipulation-numpy--pandas)
    - [Classical ML: Scikit-Learn](#classical-ml-scikit-learn)
    - [Deep learning: PyTorch](#deep-learning-pytorch)
  - [3. Compile-time commands (bytecode \& linting)](#3-compile-time-commands-bytecode--linting)
  - [4. Runtime commands (execution \& serving)](#4-runtime-commands-execution--serving)
  - [5. Debugging (tensor mismatches \& OOM kernels)](#5-debugging-tensor-mismatches--oom-kernels)
    - [Common pitfalls](#common-pitfalls)
    - [Profiling](#profiling)

---

## 1. Configuration (Windows & Linux)

Machine Learning development requires isolation of large, often conflicting dependency graphs (e.g., CUDA toolkits).

### Dependency & environment management

Never install ML packages globally. Always use `venv` or `conda`.

```bash
# Initialize an isolated virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows PowerShell

# Install the foundational ML stack
pip install numpy pandas scikit-learn jupyterlab

# Install PyTorch (The command varies severely based on target GPU compute capability)
# Example for Linux with CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Windows PATH and GPU drivers

On Windows, ensuring CUDA functionality dictates installing the NVIDIA CUDA Toolkit. The environment variable `PATH` must explicitly contain `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin` or Python will default to crawling on the CPU.

---

## 2. Writing basic Code/scripts (core ML frameworks)

Use vectorized operations backed by C libraries for array calculations that would otherwise require Python `for`-loops.

### Data manipulation: NumPy & Pandas

Pandas loads text data into tabular DataFrames, while NumPy provides the underlying numerical arrays.

```python
import numpy as np
import pandas as pd

# Load 1M rows of chaotic CSV telemetry data into RAM
df = pd.read_csv("sensor_telemetry.csv")

# Feature extraction: Drop missing data and isolate the target variable
df.dropna(inplace=True)
X = df[['temperature', 'vibration', 'pressure']].values  # Casts to a strict NumPy array
y = df['failure_status'].values

# Vectorization replaces iterating row by row. This is executed in C, 100x faster than pure Python.
X_normalized = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
```

### Classical ML: Scikit-Learn

Scikit-Learn implements the standard transformer-estimator `fit()`, `transform()`, and `predict()` API, so algorithms can share a common calling interface.

```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Split tensors into train and test blocks
X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.2)

# Instantiate and fit the model on CPU
model = RandomForestClassifier(n_estimators=100, n_jobs=-1) # -1 utilizes all CPU cores
model.fit(X_train, y_train)

# Extrapolate predictions
predictions = model.predict(X_test)
print(classification_report(y_test, predictions))
```

### Deep learning: PyTorch

When the feature complexity outstrips classical trees, PyTorch tensors take over, shifting linear algebra calculations natively to the GPU (CUDA).

```python
import torch
import torch.nn as nn
import torch.optim as optim

# Enforce hardware acceleration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class SensorNeuralNet(nn.Module):
    def __init__(self):
        super(SensorNeuralNet, self).__init__()
        self.fc1 = nn.Linear(3, 64)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        return self.sigmoid(self.fc2(self.relu(self.fc1(x))))

# Ship the model to VRAM
model = SensorNeuralNet().to(device)

# Ship the data to VRAM as FloatTensors
X_tensor = torch.FloatTensor(X_train).to(device)
y_tensor = torch.FloatTensor(y_train).view(-1, 1).to(device)

optimizer = optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.BCELoss()

# Training Loop
for epoch in range(100):
    optimizer.zero_grad()           # Clear last gradient calculations
    outputs = model(X_tensor)       # Forward pass
    loss = loss_fn(outputs, y_tensor)
    loss.backward()                 # Backpropagation
    optimizer.step()                # Adjust weights
```

---

## 3. Compile-time commands (bytecode & linting)

Python is interpreted, so it skips the traditional C++/Java linkage compilation phase. However, pre-execution bytecode caching (`.pyc` files in `__pycache__`) speeds up subsequent imports.

For production integrity, strict syntax checking and type hinting (via `mypy` or `ruff`) are needed before serving an inference model.

```bash
# Enforce PEP8 and catch syntax anomalies
pip install ruff
ruff check model_pipeline.py

# Type checking to prevent passing a string into a PyTorch FloatTensor
pip install mypy
mypy model_pipeline.py
```

---

## 4. Runtime commands (execution & serving)

Model training is a long-running blocking script, usually orchestrated by `nohup` or a workload manager. Once serialized to disk (e.g., `model.pt`), inference occurs via high-performance ASGI servers bridging to the model.

```bash
# Training Execution (Server) - Detaches the process to survive SSH drops
nohup python train_resnet.py > /var/log/training_output.log 2>&1 &

# Monitoring the GPU memory allocation continuously
watch -n 1 nvidia-smi
```

For serving the model as an API inference node using FastAPI:

```bash
# Daemonize the REST endpoint to receive prediction requests
uvicorn inference_server:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 5. Debugging (tensor mismatches & OOM kernels)

Debugging ML pipelines is an exercise in matrix algebra alignment and managing physical VRAM limits. Nothing destroys morale faster than a training loop crashing on epoch 99.

### Common pitfalls

- **Shape Mismatches:** Trying to multiply a `[32, 64]` tensor by a `[128, 64]` tensor dynamically. PyTorch throws `RuntimeError: mat1 and mat2 shapes cannot be multiplied`. Fix this by applying `.view()`, `.unsqueeze()`, or explicitly verifying dimensions with `.shape`.
- **CUDA Out of Memory (OOM):** Loading too large a batch size into your GPU. PyTorch will panic. You must either reduce `batch_size` or utilize mixed-precision training (`torch.cuda.amp`).

### Profiling

To figure out exactly which layer of your neural network is bottlenecking the compute:

```python
import torch.autograd.profiler as profiler

with profiler.profile(use_cuda=True) as prof:
    model(inputs)

print(prof.key_averages().table(sort_by="cuda_time_total"))
```

- **Tracebacks:** Check whether a tensor is on CPU or GPU. You cannot perform operations if one tensor acts locally and the other sits in physical GPU memory. PyTorch throws `Expected all tensors to be on the same device.` Fix with `.to(device)`.
