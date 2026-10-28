const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'..');
const html=fs.readFileSync(path.join(root,'dashboard/index.html'),'utf8');
// Exercise the exact function shipped in the UI, rather than a test-only copy.
const source=html.split('// HISTORY_LOGIC_START')[1].split('// HISTORY_LOGIC_END')[0];
const history=vm.runInNewContext(source+';faultHistory');
const calc=(rows,i)=>JSON.parse(JSON.stringify(history(rows,i)));
const row=(time_s,...faults)=>({time_s,faults});
test('healthy and empty replay',()=>{
 assert.deepEqual(calc([],0),[]);
 assert.deepEqual(calc([row(0),row(1)],1),[]);
});
test('persistent fault produces one episode',()=>{
 assert.deepEqual(calc([row(0,'A'),row(1,'A'),row(2,'A')],2),[
  {code:'A',started_s:0,cleared_s:null,duration_s:2}]);
});
test('first absent sample closes episode using simulation timestamps',()=>{
 assert.deepEqual(calc([row(10,'A'),row(12,'A'),row(15)],2),[
  {code:'A',started_s:10,cleared_s:15,duration_s:5}]);
});
test('recurrence creates separate episodes newest first',()=>{
 assert.deepEqual(calc([row(0,'A'),row(1),row(2,'A')],2),[
  {code:'A',started_s:2,cleared_s:null,duration_s:0},
  {code:'A',started_s:0,cleared_s:1,duration_s:1}]);
});
test('simultaneous faults close independently; duplicate codes ignored',()=>{
 assert.deepEqual(calc([row(0,'A','A','B'),row(1,'B')],1),[
  {code:'B',started_s:0,cleared_s:null,duration_s:1},
  {code:'A',started_s:0,cleared_s:1,duration_s:1}]);
});
test('backward seek hides future starts and clears; restart resets history',()=>{
 const rows=[row(0),row(1,'A'),row(2),row(3,'B')];calc(rows,3);
 assert.deepEqual(calc(rows,1),[{code:'A',started_s:1,cleared_s:null,duration_s:0}]);
 assert.deepEqual(calc(rows,0),[]);
});
test('actual simulator sample contains four completed episodes',()=>{
 const rows=fs.readFileSync(path.join(root,'data/demo.jsonl'),'utf8').trim().split(/\r?\n/).map(JSON.parse);
 assert.deepEqual(calc(rows,59),[
  {code:'SENSOR_LOSS',started_s:50,cleared_s:55,duration_s:5},
  {code:'LOW_FAN',started_s:40,cleared_s:45,duration_s:5},
  {code:'LOW_TANK',started_s:25,cleared_s:35,duration_s:10},
  {code:'BLOCKAGE',started_s:12,cleared_s:20,duration_s:8}]);
});
