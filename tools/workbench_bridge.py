"""Authenticated workbench routes on the existing local bridge."""
import secrets
from buddy.workbench.readiness import qualify_model, audit_seo
from http import HTTPStatus
from buddy.workbench.core import system_check,token_report,usage,compare_attempts,reward,ByteModel,BytePairTokenizer,microsite

def handle_workbench(handler,method,path):
    if not path.startswith('/api/local/workbench/'):return False
    host=handler.headers.get('Host','');port=handler.server.server_address[1]
    if host not in (f'localhost:{port}',f'127.0.0.1:{port}') or handler.headers.get('Origin',f'http://{host}')!=f'http://{host}':
        handler._json(HTTPStatus.FORBIDDEN,{'error':'same-origin loopback required'});return True
    if not handler.state.token or not secrets.compare_digest(handler.headers.get('Authorization',''),'Bearer '+handler.state.token):
        handler._json(HTTPStatus.UNAUTHORIZED,{'error':'local session token required'});return True
    if handler.state.paused:
        handler._json(HTTPStatus.LOCKED,{'error':'Buddy paused'});return True
    try:
        action=path.rsplit('/',1)[1]
        if method=='GET' and action=='system':result=system_check()
        elif method=='POST':
            p=handler._payload()
            if action=='qualify':result=qualify_model(p['parameters'],p.get('vocabulary',150000),p.get('hidden_size',1024),p.get('training',False),p.get('available_bytes'))
            elif action=='seo':result=audit_seo(p['html'])
            elif action=='tokens':result=token_report(p['text'])
            elif action=='bpe':
                if p.get('training_allowed') is not True or not p.get('license'):raise ValueError('training rights required')
                tokenizer=BytePairTokenizer();result={'training':tokenizer.train(p['text'],p.get('vocab_size',150001)),'inspection':tokenizer.inspect(p.get('inspect',p['text']))}
            elif action=='usage':result=usage(p['runtime_ms'],p['input_tokens'],p['output_tokens'],p.get('input_rate'),p.get('output_rate'))
            elif action=='attempts':result=compare_attempts(p['uncertainty'],p['cost_per_attempt'],p['budget'],p.get('max_attempts',8))
            elif action=='reward':result=reward(p['scores'],p['weights'],p['required'],p.get('allow_partial',False))
            elif action=='microsite':result={'html':microsite(p['region'],p['title'],p['body']),'published':False}
            elif action=='train':
                m=ByteModel();receipt=m.train(p['text'],p.get('training_allowed'),p.get('license'))
                result={'receipt':receipt,'output':m.generate(p['prompt'],p.get('length',64),p.get('temperature',1),p.get('seed',0)),'weights':{str(k):dict(v) for k,v in m.counts.items()}}
            else:raise ValueError('unknown action')
        else:raise ValueError('unknown action')
        handler._json(HTTPStatus.OK,result)
    except (ValueError,KeyError,TypeError) as e:handler._json(HTTPStatus.BAD_REQUEST,{'error':str(e)})
    return True
