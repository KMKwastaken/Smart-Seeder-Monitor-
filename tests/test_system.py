import importlib.util
import json
import os
from pathlib import Path
import subprocess
import threading
import urllib.request
from http.server import ThreadingHTTPServer
import pytest

ROOT = Path(__file__).resolve().parents[1]
@pytest.fixture(scope="session")
def binary():
    path = Path(os.environ.get("SEEDER_SIM", ROOT / "build" / ("seeder_sim.exe" if os.name == "nt" else "seeder_sim")))
    assert path.is_file(), f"Build C++ first; missing {path} (or set SEEDER_SIM)"
    return str(path.resolve())

def run(binary, *args):
    return subprocess.run([binary, *map(str,args)], capture_output=True, text=True, timeout=10)
def records(binary, *args):
    p=run(binary,*args); assert p.returncode==0,p.stderr
    return [json.loads(line) for line in p.stdout.splitlines()]

def test_nominal_schema_and_repeatability(binary):
    a=records(binary,'--scenario','normal','--ticks',20)
    assert a==records(binary,'--scenario','normal','--ticks',20)
    assert [r['tick'] for r in a]==list(range(20))
    assert all(r['simulated'] and r['schema']==1 and not r['faults'] for r in a)

@pytest.mark.parametrize('scenario,fault',[('low-tank','LOW_TANK'),('low-fan','LOW_FAN'),('sensor-loss','SENSOR_LOSS')])
def test_fault_injection(binary,scenario,fault):
    assert all(r['faults']==[fault] for r in records(binary,'--scenario',scenario,'--ticks',4))

def test_debounce_and_recovery(binary):
    a=records(binary,'--scenario','demo')
    assert a[10]['faults']==a[11]['faults']==[]
    assert a[12]['faults']==a[19]['faults']==['BLOCKAGE']
    assert a[20]['faults']==[]
    assert a[50]['faults']==['SENSOR_LOSS'] and a[55]['faults']==[]

@pytest.mark.parametrize('values,expected',[
    ((8,4.99,15,2000,1),['BLOCKAGE']),
    ((8,5,15,2000,1),[]),
    ((1,0,15,0,1),[]),
    ((8,0,14.99,1999,1),['BLOCKAGE','LOW_TANK','LOW_FAN']),
    ((8,0,10,100,0),['SENSOR_LOSS']),
    ((8,-1,10,100,1),['INVALID_SENSOR']),
    ((0,0,80,0,1),[]),
])
def test_boundaries_and_priority(binary,values,expected):
    assert records(binary,'--probe',*values,'--ticks',3)[-1]['faults']==expected

@pytest.mark.parametrize('args',[['--ticks',0],['--ticks',100001],['--ticks','2junk'],['--scenario','bad'],['--unknown'],['--probe',8,'nan',80,3200,1]])
def test_bad_cli(binary,args):
    p=run(binary,*args);assert p.returncode==2 and 'Error:' in p.stderr

def test_sample_matches_cpp(binary):
    expected=[json.loads(s) for s in (ROOT/'data/demo.jsonl').read_text().splitlines()]
    assert records(binary,'--scenario','demo')==expected

def test_http_and_rejected_data(tmp_path):
    spec=importlib.util.spec_from_file_location('dashboard_server',ROOT/'dashboard/server.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    rows=module.load_records(ROOT/'data/demo.jsonl')
    bad=tmp_path/'bad.jsonl';bad.write_text('{"schema":1,"simulated":false}')
    with pytest.raises(ValueError):module.load_records(bad)
    server=ThreadingHTTPServer(('127.0.0.1',0),module.make_handler(rows))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        url=f'http://127.0.0.1:{server.server_port}'
        with urllib.request.urlopen(url+'/api/telemetry') as response:assert json.load(response)==rows
        with urllib.request.urlopen(url) as response:assert b'SIMULATED DATA ONLY' in response.read()
        with pytest.raises(urllib.error.HTTPError) as error:urllib.request.urlopen(url+'/../README.md')
        assert error.value.code==404
    finally:server.shutdown();server.server_close();thread.join()
