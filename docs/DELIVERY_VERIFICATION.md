# Delivery verification — October 28, 2026

Verified on Windows using Python 3.12.14, pytest 9.2.0 and the Zig 0.16.0 C++ toolchain:
- Compiled the actual C++17 source to a Windows executable.
- Generated the included 60-record data/demo.jsonl from that executable.
- Ran the full pytest suite: **20 passed**, no skipped tests.
- Suite includes real loopback HTTP requests and compiled-executable integration tests.
- Included machine-readable JUnit report under docs/test-results.xml.

The compiler emitted warnings from its bundled C++ standard library during its first build. It completed successfully. CMake itself was unavailable locally, so compilation used the compiler directly. Linux CMake build and .NET 8 build/replay are configured in GitHub Actions but were not run on GitHub in this delivery. The local machine has a .NET runtime but no SDK; the C# monitor has not been compiled locally. Visual browser interaction has not been manually verified; the documented manual acceptance procedure remains available. JavaScript syntax was checked with Node.

The ZIP includes source, sample telemetry, documentation, tests and CI configuration. It excludes generated binaries, caches and downloaded development tools. Python alone runs the included browser replay; C++ compilation is needed to generate new scenarios. No hardware or field validation was performed.

## Fault history update verification

Seven Node.js history tests passed, exercising the exact function embedded in the dashboard. JavaScript syntax check passed. The 19 C++ regression tests passed again; the HTTP test was excluded on this update because local network access is restricted in the current execution environment (the original delivery's HTTP check passed). The new Node test step is included in GitHub Actions. Updated graphical behavior has not been checked in an interactive browser. See VALIDATION.md for the time-slider acceptance steps.
