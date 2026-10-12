from types import SimpleNamespace
from tools.workbench_bridge import handle_workbench

class Handler:
    def __init__(self,payload=None,headers=None):
        self.headers={'Host':'localhost:4321','Origin':'http://localhost:4321','Authorization':'Bearer local-test',**(headers or {})}
        self.server=SimpleNamespace(server_address=('127.0.0.1',4321));self.state=SimpleNamespace(token='local-test',paused=False);self.payload=payload;self.response=None
    def _payload(self):return self.payload
    def _json(self,status,body):self.response=(int(status),body)

def test_auth_origin_and_pause():
    for headers,status in [({'Authorization':''},401),({'Origin':'https://evil.example'},403),({'Host':'evil.example'},403)]:
        h=Handler(headers=headers);handle_workbench(h,'GET','/api/local/workbench/system');assert h.response[0]==status
    h=Handler();h.state.paused=True;handle_workbench(h,'GET','/api/local/workbench/system');assert h.response[0]==423

def test_rights_and_real_training():
    h=Handler({'text':'hello hello','prompt':'h','training_allowed':False,'license':'owned'});handle_workbench(h,'POST','/api/local/workbench/train');assert h.response[0]==400
    h.payload['training_allowed']=True;handle_workbench(h,'POST','/api/local/workbench/train');assert h.response[0]==200;assert h.response[1]['weights']

def test_no_arbitrary_execution_endpoint():
    h=Handler({'command':'danger'});handle_workbench(h,'POST','/api/local/workbench/exec');assert h.response[0]==400
