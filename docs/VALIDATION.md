# Repeatable validation procedure

Build C++ and run `python -m pytest -q`. Tests require the actual compiled binary; missing builds fail rather than silently skip. Override its location with SEEDER_SIM. Tests cover deterministic output, schema, injected faults, debounce delay, recovery, exact threshold edges, stationary suppression, simultaneous faults, diagnostic priority, invalid CLI inputs, nonfinite input, sample-file parity, and real HTTP responses including traversal rejection.

Manual dashboard acceptance: start server; verify prominent simulation notice; pause at tick 11 (no blockage), advance slider to 12 (BLOCKAGE), then 20 (cleared). Inspect low tank at 25, low fan at 40, sensor loss at 50 with hidden readings, recovery at 55. Restart, play, resize to phone width, and verify keyboard access to buttons and time slider. Disconnect intervals should have gaps in the flow plot. Change `--port` if 8080 is occupied.

C# acceptance: build with SDK 8 and run sample file. Expect 60 samples and 28 samples with active faults (8 blockage + 10 low tank + 5 low fan + 5 disconnected). Missing/invalid files return exit code 2. CI validates the C# compile and successful replay; it does not perform browser UI automation.

Hardware/field validation is NOT performed. A future procedure would require reviewed sensor specifications, calibrated reference inputs, fault insertion equipment, timestamp/freshness checks, captured traces, environmental testing and supervised field observation. Simulated tests do not establish equipment safety or agronomic correctness.

## Fault history acceptance

At tick 12, BLOCKAGE starts with 0 s elapsed. At 19 it remains active with 7 s elapsed. At 20 it shows Cleared 20 s and 8 s elapsed. At 59 there are four completed episodes: blockage 12–20, low tank 25–35, low fan 40–45, sensor loss 50–55. Seek back to 12: later episodes and the future clear time must disappear. Restart: no episodes. Separate Node tests exercise these transitions, recurrence and simultaneous faults against the function shipped in the dashboard.
