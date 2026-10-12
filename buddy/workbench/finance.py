"""Offline money records and paper orders. Never transmits funds or broker orders."""
import sqlite3,json,hashlib
from decimal import Decimal

class Ledger:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS journal(tenant TEXT,id TEXT,digest TEXT,body TEXT,PRIMARY KEY(tenant,id))')
    def post(self,tenant,id,currency,entries):
        if not tenant or not id or not isinstance(currency,str) or len(currency)!=3 or not currency.isalpha():raise ValueError('tenant, id, currency required')
        if len(entries)<2 or any(not e.get('account') or type(e.get('cents')) is not int for e in entries):raise ValueError('integer double-entry records required')
        if sum(e['cents'] for e in entries)!=0:raise ValueError('unbalanced transaction')
        body=json.dumps({'currency':currency.upper(),'entries':entries},sort_keys=True);digest=hashlib.sha256(body.encode()).hexdigest()
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO journal VALUES(?,?,?,?)',(tenant,id,digest,body))
            previous=self.db.execute('SELECT digest FROM journal WHERE tenant=? AND id=?',(tenant,id)).fetchone()[0]
            if previous!=digest:raise ValueError('idempotency conflict')
        return {'id':id,'recorded':True,'funds_moved':False}
    def balances(self,tenant,currency):
        result={}
        for (body,) in self.db.execute('SELECT body FROM journal WHERE tenant=?',(tenant,)):
            r=json.loads(body)
            if r['currency']!=currency.upper():continue
            for e in r['entries']:result[e['account']]=result.get(e['account'],0)+e['cents']
        return result

def paper_order(symbol,side,quantity,price,max_notional):
    if not isinstance(symbol,str) or not symbol.isascii() or not symbol.replace('.','').isalnum() or len(symbol)>15:raise ValueError('invalid symbol')
    if side not in ('buy','sell'):raise ValueError('buy or sell required')
    values=[]
    for x in (quantity,price,max_notional):
        if isinstance(x,bool):raise ValueError('numeric values required')
        d=Decimal(str(x))
        if not d.is_finite() or d<=0:raise ValueError('positive finite values required')
        values.append(d)
    q,p,limit=values
    if q*p>limit:raise ValueError('paper risk limit exceeded')
    return {'symbol':symbol.upper(),'side':side,'quantity':str(q),'price':str(p),'notional':str(q*p),'status':'paper_simulation','submitted_to_broker':False,'fill_verified':False}
