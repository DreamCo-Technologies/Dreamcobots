import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

function worker() {
 const messages=[];
 const context={self:{location:{origin:'https://dreamco-technologies.github.io'},postMessage:value=>messages.push(value)}};
 vm.runInNewContext(readFileSync('website/buddy-model-worker.js','utf8'),context);
 return {context,messages};
}

test('worker rejects foreign origins and malformed messages before loading or inference',async()=>{
 const {context,messages}=worker();
 await context.self.onmessage({origin:'https://foreign.invalid',data:{type:'load'}});
 await context.self.onmessage({origin:'https://foreign.invalid',data:{type:'run',prompt:'untrusted'}});
 for(const data of [null,'run',{}, {type:'unsupported'}])await context.self.onmessage({origin:'',data});
 assert.deepEqual(messages,[]);
});

test('dedicated-worker and same-origin messages retain model-not-loaded recovery',async()=>{
 const {context,messages}=worker();
 for(const origin of ['',context.self.location.origin])await context.self.onmessage({origin,data:{type:'run',prompt:'hello'}});
 assert.equal(messages.length,2);
 assert.ok(messages.every(message=>message.type==='error'&&message.message==='Load the model first'));
});
