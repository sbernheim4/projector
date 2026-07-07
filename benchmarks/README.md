# Benchmarks

This folder contains small dependency-free benchmarks for Projector overhead.

Run from the repository root:

```bash
PYTHONPATH=src .venv/bin/python benchmarks/benchmark_projector.py
```

Or use the repo helper:

```bash
just benchmark
```

The benchmark operation is constructing one output payload object from a
JSON-like dictionary. That is the model-specific hot path an HTTP request would
pay when parsing or shaping request/response data. A full HTTP benchmark would
mostly measure FastAPI, routing, test-client, and networking overhead rather
than Projector itself.

The benchmark compares homogeneous input/output paths against manually defined
classes:

- Pydantic -> Pydantic
- dataclass -> dataclass
- attrs -> attrs
- `TypedDict` -> `TypedDict`

For each path, the hot-path benchmark compares:

- a manual factory or constructor for the target shape
- the equivalent Projector factory returned by `project(...)`

It also measures one-time `project(...)` model generation cost for each renderer.

Current interpretation from local runs:

- Pydantic -> Pydantic adds little overhead relative to Pydantic validation.
- dataclass -> dataclass and attrs -> attrs currently add significant overhead
  because Projector recursively converts nested dictionaries on every factory
  call.
- `TypedDict` -> `TypedDict` has low absolute overhead, but the ratio is visible
  because the manual baseline is just dictionary construction.

Interpretation:

- Per-instance validation is the hot path for request/response payloads.
- `project(...)` is startup/configuration cost if users define projected models
  at import time.
- Ratios matter less than absolute time for very cheap targets like `TypedDict`.
