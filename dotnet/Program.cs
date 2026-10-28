using System.Text.Json;
// Optional cross-platform console dashboard; no NuGet packages needed.
if (args.Length != 1) { Console.Error.WriteLine("Usage: dotnet run --project dotnet -- data/demo.jsonl"); return 2; }
try {
 Console.WriteLine("SMART SEEDER — SIMULATED DATA ONLY");
 int count = 0, faultSamples = 0;
 foreach (string line in File.ReadLines(args[0])) {
  if (string.IsNullOrWhiteSpace(line)) continue;
  using var doc = JsonDocument.Parse(line); var r = doc.RootElement;
  if (!r.GetProperty("simulated").GetBoolean() || r.GetProperty("schema").GetInt32()!=1)
   throw new InvalidDataException("Expected simulated schema 1 telemetry");
  var faults = r.GetProperty("faults").EnumerateArray().Select(f => f.GetString()).ToArray();
  count++; if (faults.Length > 0) faultSamples++;
  Console.WriteLine($"t={r.GetProperty("time_s")} s | flow={r.GetProperty("flow_seeds_s")} seeds/s | tank={r.GetProperty("tank_pct")}% | {string.Join(", ", faults.DefaultIfEmpty("OK"))}");
 }
 if (count == 0) throw new InvalidDataException("No telemetry records");
 Console.WriteLine($"Samples: {count}; samples with active faults: {faultSamples}"); return 0;
} catch (Exception e) when (e is IOException or JsonException or InvalidDataException or KeyNotFoundException or InvalidOperationException) {
 Console.Error.WriteLine($"Cannot replay telemetry: {e.Message}"); return 2;
}
