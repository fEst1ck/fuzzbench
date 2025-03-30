#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import sys

if len(sys.argv) != 2:
    print("Usage: python plot_fuzzer_stats.py <fuzzer_stats.json>")
    sys.exit(1)

json_file = sys.argv[1]

with open(json_file, "r") as f:
    data = json.load(f)

# Extract time and metrics
time = [entry["runtime_seconds"] for entry in data]
executions = [entry["total_executions"] for entry in data]
queue_size = [entry["queue_size"] for entry in data]
crashes = [entry["crash_count"] for entry in data]

# Coverage types
coverage_block = [entry["coverage_count"]["block"] for entry in data]
coverage_edge = [entry["coverage_count"]["edge"] for entry in data]
coverage_path = [entry["coverage_count"]["path"] for entry in data]

# --- Individual plots ---

# Block Coverage
plt.figure()
plt.plot(time, coverage_block)
plt.xlabel("Runtime (s)")
plt.ylabel("Block Coverage")
plt.title("Block Coverage Over Time")
plt.grid(True)

# Edge Coverage
plt.figure()
plt.plot(time, coverage_edge)
plt.xlabel("Runtime (s)")
plt.ylabel("Edge Coverage")
plt.title("Edge Coverage Over Time")
plt.grid(True)

# Path Coverage
plt.figure()
plt.plot(time, coverage_path)
plt.xlabel("Runtime (s)")
plt.ylabel("Path Coverage")
plt.title("Path Coverage Over Time")
plt.grid(True)

# Total Executions
plt.figure()
plt.plot(time, executions)
plt.xlabel("Runtime (s)")
plt.ylabel("Total Executions")
plt.title("Total Executions Over Time")
plt.grid(True)

# Queue Size
plt.figure()
plt.plot(time, queue_size, color='orange')
plt.xlabel("Runtime (s)")
plt.ylabel("Queue Size")
plt.title("Queue Size Over Time")
plt.grid(True)

# Crash Count
plt.figure()
plt.plot(time, crashes, color='red')
plt.xlabel("Runtime (s)")
plt.ylabel("Crash Count")
plt.title("Crash Count Over Time")
plt.grid(True)

plt.show()

