# Internship alignment and demo

Source: the user's Bourgault Application Support handoff retrieved from the referenced conversation. It emphasizes C/C++/C#, Python, unit/integration testing, debugging, Linux and Visual Studio/VS Code, documentation/code review, hardware integration and prototype/field validation. The full job posting was not provided; no additional employer requirements are asserted.

C++ sensor modeling and a stateful detector demonstrate firmware-adjacent logic. Python pytest drives the compiled executable and checks boundaries and recovery. The browser UI makes diagnoses inspectable, and the optional C# console client demonstrates a second consumer of the shared contract. CMake/Linux instructions and GitHub Actions support repeatable builds. Architecture and validation documents make assumptions and limits reviewable.

Suggested five-minute demo: introduce the simulation boundary; run the dashboard; inspect the first blockage and recovery; show the three-sample debounce in C++; run pytest; show CI configuration; explain how a timestamped hardware adapter would replace the generator. The demo demonstrates a development approach, not completed hardware or field integration.

Possible resume wording after personally reviewing and running the project: “Developed a simulated seeder monitoring portfolio project with C++ fault detection, a cross-platform telemetry dashboard, C# replay tooling, and Python integration tests; documented Linux build and CI workflows.” Do not claim real equipment deployment, team collaboration, measured uptime improvements, or field validation from this project.

Review checklist: verify units and strict comparison boundaries; inspect reset behavior after stopped/disconnected samples; confirm schema compatibility; review tests before modifying thresholds; discuss tradeoffs of immediate recovery versus hysteresis. Next extensions: separate detector library, timestamp-based debounce, C# graphical UI, multi-row faults, bounded streaming replay and schema validation.
