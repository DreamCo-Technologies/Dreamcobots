import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync('website/device-backend.html','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)[1];
function setup(){
 const elements=new Map();const data=new Map();
 const document={getElementById(id){if(!elements.has(id))elements.set(id,{value:'',checked:false,replaceChildren(...children){this.children=children;}});return elements.get(id);},createElement(){return {textContent:''};}};
 const context=vm.createContext({document,localStorage:{getItem:k=>data.get(k),setItem:(k,v)=>data.set(k,v),removeItem:k=>data.delete(k)},crypto:{randomUUID:()=> 'fixture-device'}});
 vm.runInContext(script,context);return {context,document,data};
}
test('untrusted stored fields render as text and permissions default off',()=>{
 const {context,document}=setup();
 vm.runInContext(`const s=load();s.users=[{name:'<img src=x onerror=alert(1)>',role:'owner'}];s.admin.notes=['<script>alert(1)</script>'];save(s);render();`,context);
 assert.equal(document.getElementById('users').children[0].textContent,'<img src=x onerror=alert(1)> · owner');
 assert.equal(document.getElementById('users').innerHTML,undefined);
 assert.equal(document.getElementById('scopeEvents').checked,false);
});
test('event writes and admin notes obey local consent',()=>{
 const {context,document}=setup();
 document.getElementById('epayload').value='private';vm.runInContext('logEvent()',context);
 assert.equal(vm.runInContext('load().events.length',context),0);
 document.getElementById('scopeEvents').checked=true;vm.runInContext('saveScopes();logEvent()',context);
 assert.equal(vm.runInContext('load().events.length',context),2);
 document.getElementById('knowledge').value='private';vm.runInContext('saveAdmin()',context);
 assert.equal(vm.runInContext('load().admin.notes.length',context),0);
});
