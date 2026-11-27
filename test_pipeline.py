import csv, json, tempfile, unittest, io, contextlib
from pathlib import Path
from src.pipeline import validate_data, build, sha256
from src.contracts import check_response
class TestData(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.f=Path(self.t.name)/'test.csv'
  self.f.write_text('id,texto,clase_real\n1,Consulta al folio 123,INDIVIDUAL\n2,Consulta varios folios,PAQUETE\n',encoding='utf-8')
 def tearDown(self):self.t.cleanup()
 def test_ok(self):self.assertEqual(validate_data(self.f)['filas'],2)
 def test_duplicate(self):
  self.f.write_text('id,texto,clase_real\n1,x,INDIVIDUAL\n1,y,PAQUETE\n')
  with self.assertRaises(ValueError):validate_data(self.f)
 def test_missing(self):
  self.f.write_text('id,texto\n1,x\n')
  with self.assertRaises(ValueError):validate_data(self.f)
 def test_bad_label(self):
  self.f.write_text('id,texto,clase_real\n1,x,OTRA\n')
  with self.assertRaises(ValueError):validate_data(self.f)
 def test_manifest(self):
  with tempfile.TemporaryDirectory() as o:
   with contextlib.redirect_stdout(io.StringIO()):
    result=build(Path(o),self.f,Path(o)/'out','v-demo')
   self.assertTrue((Path(o)/'out'/'manifest.json').exists())
   self.assertFalse(result['automatic_deployment_executed'])
class TestContract(unittest.TestCase):
 def payload(self):return {'clase_predicha':'INDIVIDUAL','decision_operativa':'REVISION_HUMANA','requiere_revision_humana':True,'puntaje_individual':.25,'umbral_individual':.276334,'version_modelo':'v1','advertencia':'demo'}
 def test_valid(self):self.assertTrue(check_response(self.payload()))
 def test_missing(self):
  p=self.payload();del p['advertencia']
  with self.assertRaises(ValueError):check_response(p)
 def test_invalid_eligibility(self):
  p=self.payload();p.update(decision_operativa='FLUJO_INDIVIDUAL',requiere_revision_humana=False)
  with self.assertRaises(ValueError):check_response(p)
 def test_valid_eligibility(self):
  p=self.payload();p.update(decision_operativa='FLUJO_INDIVIDUAL',requiere_revision_humana=False,puntaje_individual=.8)
  self.assertTrue(check_response(p))
if __name__=='__main__':unittest.main()
