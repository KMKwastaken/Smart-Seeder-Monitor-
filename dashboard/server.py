"""Local, read-only simulator replay. Standard library only."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def load_records(path):
    records = [json.loads(line) for line in Path(path).read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not records or any(r.get("simulated") is not True or r.get("schema") != 1 for r in records):
        raise ValueError("Expected nonempty schema 1 simulated telemetry")
    return records

def make_handler(records):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/api/telemetry":
                body = json.dumps(records).encode(); content = "application/json"
            elif self.path in ("/", "/index.html"):
                body = (ROOT / "index.html").read_bytes(); content = "text/html; charset=utf-8"
            else:
                self.send_error(404); return
            self.send_response(200)
            self.send_header("Content-Type", content)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers(); self.wfile.write(body)
    return Handler

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT.parent / "data/demo.jsonl")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    records = load_records(args.data)
    with ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(records)) as server:
        print(f"SIMULATION ONLY — http://127.0.0.1:{args.port}", flush=True)
        try: server.serve_forever()
        except KeyboardInterrupt: pass
