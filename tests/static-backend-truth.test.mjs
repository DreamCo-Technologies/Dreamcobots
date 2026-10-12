import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
test('offline command center never reports live backend or success for missing write',async()=>{
 let source=fs.readFileSync('website/command-center/app.js','utf8');source=source.replace(/render\(\);\s*$/,'');
 const context={window:{},fetch:async()=>({json:async()=>[]}),console,document:{getElementById:()=>({innerHTML:''})},localStorage:{getItem:()=>null,setItem:()=>{}}};vm.createContext(context);vm.runInContext(source,context);
 const health=await context.localApi('/api/health');assert.equal(health.status,'backend_disconnected');
 const write=await context.localApi('/api/unimplemented',{method:'POST'});assert.equal(write.ok,false);
 const capabilities=await context.localApi('/api/capabilities');assert.ok(capabilities.capabilities.every(c=>c.status!=='live'));
});
