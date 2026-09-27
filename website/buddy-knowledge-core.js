/* Local retrieval and measurable knowledge access; never model-weight training. */
(function(root) {
  'use strict';
  function terms(text) { return [...new Set(String(text).toLowerCase().match(/[\p{L}\p{N}]{2,}/gu) || [])]; }
  function source(text, label, reference, allowed) {
    if (!allowed) throw Error('Confirm that you may use this material before adding it.');
    if (typeof text !== 'string' || text.trim().length < 20 || text.length > 200000) throw Error('Use 20–200,000 characters of plain text.');
    if (!String(label).trim()) throw Error('Give this source a name.');
    let url = '';
    if (reference) { const parsed = new URL(reference); if (!['https:', 'http:'].includes(parsed.protocol) || parsed.username || parsed.password) throw Error('Use a public HTTP(S) reference without credentials.'); url = parsed.href; }
    const chunks = text.trim().match(/[\s\S]{1,1600}/g).map((content, i) => ({id:i + 1, text:content, terms:terms(content)}));
    return {label:String(label).trim().slice(0,160), reference:url, authorized_by_user:true, chunks};
  }
  function retrieve(sources, question, limit=3) {
    const query=terms(question); if (!query.length) return [];
    return sources.flatMap((s, index) => s.chunks.map(c => ({source:index, label:s.label, reference:s.reference, chunk:c.id, text:c.text, score:query.filter(t=>c.terms.includes(t)).length / query.length})))
      .filter(r=>r.score>0).sort((a,b)=>b.score-a.score || a.source-b.source || a.chunk-b.chunk).slice(0,limit);
  }
  function compare(before, after, question, expected) {
    if (terms(question).length<2 || String(expected).trim().length<3) throw Error('Enter a specific question and an expected phrase of at least 3 characters.');
    const grade = sources => { const results=retrieve(sources,question,1); return {passed:results.length>0 && results[0].text.toLowerCase().includes(expected.trim().toLowerCase()), results}; };
    const baseline=grade(before), current=grade(after);
    return {schema:'dreamco.local_retrieval_evidence.v1', question, expected_phrase:expected.trim(), baseline, current, improved:!baseline.passed && current.passed, model_weights_changed:false, scope:'User-authored single-case retrieval check; not a hidden holdout, independent benchmark, or general model intelligence test.'};
  }
  const api={source,retrieve,compare};
  if (typeof module!=='undefined' && module.exports) module.exports=api;
  else root.BuddyKnowledge=api;
})(typeof globalThis!=='undefined'?globalThis:this);
