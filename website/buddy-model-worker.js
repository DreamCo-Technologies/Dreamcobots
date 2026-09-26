/* A dedicated worker keeps inference off the page's main thread. */
const MODEL='HuggingFaceTB/SmolLM2-135M-Instruct';
const REVISION='12fd25f77366fa6b3b4b768ec3050bf629380bac';
let generator;
self.onmessage=async({data})=>{
 try {
  if(data.type==='load'){
   const {pipeline,env}=await import('https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.8.1/dist/transformers.min.js');
   env.allowLocalModels=false;env.backends.onnx.wasm.numThreads=1;
   generator=await pipeline('text-generation',MODEL,{revision:REVISION,device:'wasm',dtype:'q4',progress_callback:info=>{if(info.status==='progress')self.postMessage({type:'progress',file:info.file,progress:info.progress});}});
   self.postMessage({type:'ready',model:MODEL,revision:REVISION});
  } else if(data.type==='run'){
   if(!generator)throw Error('Load the model first');
   const prompt=String(data.prompt||'').slice(0,2000);if(!prompt.trim())throw Error('Enter a prompt');const started=performance.now();
   const result=await generator([{role:'system',content:'You are Buddy, a concise beginner coding assistant. State uncertainty. Do not claim to have performed external actions.'},{role:'user',content:prompt}],{max_new_tokens:128,do_sample:false,repetition_penalty:1.15,no_repeat_ngram_size:4});
   const text=result[0].generated_text;const output=Array.isArray(text)?text.at(-1).content:String(text);
   self.postMessage({type:'result',record:{model:MODEL,revision:REVISION,library:'@huggingface/transformers@3.8.1',device:'wasm',dtype:'q4',prompt,output,elapsed_ms:Math.round(performance.now()-started),created_at:new Date().toISOString(),quality_verified:false,execution:'local_model_inference',external_actions_executed:false}});
  }
 }catch(error){self.postMessage({type:'error',message:error.message||String(error)});}
};
