"""Optional online smoke test. No production decision. Needs explicit --url argument."""
import argparse, json, time, urllib.request, urllib.error
from .contracts import check_response

def get(url):
    with urllib.request.urlopen(url.rstrip('/')+'/health',timeout=25) as r:
        return r.status,json.loads(r.read().decode())

def predict(url,text):
    body=json.dumps({'texto':text}).encode('utf-8')
    req=urllib.request.Request(url.rstrip('/')+'/predict', data=body, headers={'Content-Type':'application/json'}, method='POST')
    with urllib.request.urlopen(req,timeout=25) as r:
        return r.status,json.loads(r.read().decode())

def main():
    p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--predict',action='store_true');a=p.parse_args()
    st,time0=get(a.url);assert st==200 and time0.get('status')=='ok' and time0.get('model_loaded') is True
    print('[OK] Health responde y modelo cargado')
    if a.predict:
        st,res=predict(a.url,'Solicito confirmar el pago asociado al folio sintetico 12345.')
        assert st==200 and check_response(res)
        print('[OK] Contrato de clasificacion; resultado informativo:',res['clase_predicha'],res['decision_operativa'])
if __name__=='__main__':main()
