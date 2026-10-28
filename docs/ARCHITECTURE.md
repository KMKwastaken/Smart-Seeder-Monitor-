# Architecture and telemetry contract

Data flow: C++ virtual sensors → stateful C++ fault detector → JSON Lines file → Python HTTP replay server → browser dashboard. The optional C# client independently reads the same file. The UI displays detector outputs; it does not implement a second detector.

One virtual metering channel is sampled at 1 Hz. All channels are synthetic. JSON schema version 1 fields: `schema` (integer 1), `simulated` (true), `tick` (zero-based sequence), `time_s` (simulation seconds), `speed_kph`, `flow_seeds_s`, `tank_pct`, `fan_rpm` (finite numeric values), `connected` (boolean), `faults` (array of active code strings). Disconnected numeric values must be treated as unavailable; UI hides them. JSONL allows streaming but this dashboard loads the entire file once. The 100,000-sample CLI limit bounds generated runs; use small replays for responsive charting.

Detector order:
1. Disconnected → SENSOR_LOSS only; reset blockage counter.
2. Negative speed, flow, RPM or tank outside [0,100] → INVALID_SENSOR only; reset counter.
3. Moving means speed strictly above 1 km/h. Flow strictly below 5 seeds/s for three consecutive moving samples → BLOCKAGE. A healthy or stopped sample clears immediately.
4. Tank strictly below 15% → LOW_TANK, even when stopped.
5. Moving and RPM strictly below 2000 → LOW_FAN.

Non-finite input is rejected before JSON serialization. Thresholds and timing are illustrative. Current debounce assumes exactly one-second samples and does not handle irregular timestamps. There is no hysteresis, alarm latching, event persistence, stale-time detection, multi-row addressing, calibration, CAN/ISOBUS parsing, or real-time scheduler. Normal values vary by deterministic sine wave; no randomness or physical seed-rate model is claimed.

Future hardware adapter boundary: replace Reading generation with a timestamped acquisition adapter; validate units, range, freshness, CRC/message integrity and sequence; feed detector only with quality-qualified readings. Establish actual requirements, hazard analysis, watchdog behavior, hardware-in-loop tests and supervised field validation with engineers before considering any equipment use. This repository deliberately has no control path.

Server binds only loopback and serves exactly `/`, `/index.html`, and `/api/telemetry`; it does not expose arbitrary files. It is a local development server, without authentication or production deployment features. C++ input and server data are trusted local development inputs, not a hardened ingestion boundary.

## Fault episode history

The browser reconstructs episodes from the loaded telemetry prefix through the selected sample. Each code absent-to-present transition starts an episode; the first subsequent absent sample closes it. Elapsed duration is clear/current simulation time minus start time. A code already active in the first sample starts at that sample, without claiming an earlier onset. Episodes still active at replay end stay Active. Diagnostic suppression can end an episode without proving physical recovery. Recomputing on seek/restart avoids duplicate entries and future-data leakage. No new fault detection rules, persistence, or control actions are added.
