import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';

test('prompt chaining renders its initial and fetched techniques and filters them', async () => {
  const html=fs.readFileSync('website/prompt-chaining.html','utf8');
  const source=html.match(/<script>([\s\S]*?)<\/script>/)[1];
  const nodes=new Map();
  const node=()=>({children:[],value:'',textContent:'',handlers:{},appendChild(child){this.children.push(child);},addEventListener(event,handler){this.handlers[event]=handler;}});
  for(const id of ['chains','chain-search','chain-filter']) nodes.set(id,node());
  Object.defineProperty(nodes.get('chains'),'textContent',{set(){this.children=[];}});
  let requests=0;
  const context={document:{getElementById:id=>nodes.get(id),createElement:()=>node()},
    fetch:async()=>({json:async()=>({techniques:[++requests===1?'extra method':'advanced method']})})};
  vm.runInNewContext(source,context);
  assert.equal(nodes.get('chains').children.length,28);
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(nodes.get('chains').children.length,30);
  nodes.get('chain-search').value='EXTRA';nodes.get('chain-filter').handlers.click();
  assert.equal(nodes.get('chains').children.length,1);
  assert.equal(nodes.get('chains').children[0].textContent,'extra method');
});
