import unittest
from src.monitor import summarize
from src.common import percentile_nearest_rank, public_base

class TestMonitor(unittest.TestCase):
    def test_percentil(self):
        self.assertEqual(percentile_nearest_rank([1,2,3,4,5],.95),5)
        self.assertIsNone(percentile_nearest_rank([],.95))

    def test_resumen(self):
        records=[
            {"endpoint":"/health","status":200,"ok":True,"duration_ms":20,"warmup":True},
            {"endpoint":"/health","status":503,"ok":False,"duration_ms":100,"warmup":False},
            {"endpoint":"/predict","status":200,"ok":True,"duration_ms":50,"warmup":False,"clase_esperada":"PAQUETE","decision_operativa":"REVISION_HUMANA"},
            {"endpoint":"/predict","status":200,"ok":True,"duration_ms":100,"warmup":False,"clase_esperada":"AMBIGUA","decision_operativa":"ACEPTACION_AUTOMATICA"},
        ]
        s=summarize(records)
        self.assertEqual(s["n_ventana"],2)
        self.assertEqual(s["disponibilidad"],.5)
        self.assertEqual(s["error_5xx_rate"],.25)
        self.assertEqual(s["falsas_elegibilidades"],1)
        self.assertEqual(s["latencia_p95_ms"],100)

    def test_url(self):
        self.assertEqual(public_base("https://example.com/health"),"https://example.com")
        with self.assertRaises(ValueError):public_base("file:///etc/passwd")

if __name__=="__main__":unittest.main()
