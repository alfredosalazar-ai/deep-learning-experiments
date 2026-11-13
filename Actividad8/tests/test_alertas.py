import unittest
from datetime import datetime, timedelta, timezone
from src.alertas import evaluar_alertas, deduplicar
from src.common import load_config
from src.incidentes import simular_incidentes

class TestAlertas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.config=load_config()

    def test_slo_trigger(self):
        m={"n_ventana":50,"disponibilidad":.80,"error_5xx_rate":.20,
           "latencia_p95_ms":6000,"n_latencia":30,
           "falsas_elegibilidades":1,"drift_psi":.6,"n_drift":100}
        result=evaluar_alertas(m,self.config)
        self.assertEqual(len(result),5)
        self.assertIn("FALSA_ELEGIBILIDAD",[r["codigo"] for r in result])

    def test_small_sample_suppressed(self):
        m={"n_ventana":1,"disponibilidad":0,"error_5xx_rate":1,"latencia_p95_ms":7000,"n_latencia":1}
        self.assertEqual(evaluar_alertas(m,self.config),[])

    def test_cooldown(self):
        now=datetime(2026,11,12,tzinfo=timezone.utc)
        alert={"codigo":"LATENCIA_P95","severidad":"P2"}
        pub,state=deduplicar([alert],{},30,now)
        self.assertEqual(len(pub),1)
        pub2,_=deduplicar([alert],state,30,now+timedelta(minutes=15))
        self.assertEqual(len(pub2),0)
        pub3,_=deduplicar([alert],state,30,now+timedelta(minutes=31))
        self.assertEqual(len(pub3),1)

    def test_simulated_recovery(self):
        data=simular_incidentes(self.config)
        self.assertEqual(len(data["incidentes"]),3)
        self.assertTrue(all(x["recuperacion_simulada"] for x in data["incidentes"]))
        self.assertFalse(data["modelo_en_render_modificado"])

if __name__=="__main__":unittest.main()
