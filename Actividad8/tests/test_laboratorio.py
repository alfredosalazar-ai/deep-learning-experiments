import unittest
from src.common import load_config
from src.laboratorio import ejecutar_laboratorio, consola
from src.calidad import evaluar_pares, demo_pares, alerta_calidad

class TestLaboratorio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e=ejecutar_laboratorio(load_config())

    def test_incidentes_con_accion_real_en_estado_local(self):
        self.assertEqual(len(self.e['incidentes']),3)
        self.assertTrue(all(x['recuperacion_verificada'] for x in self.e['incidentes']))
        self.assertEqual(self.e['incidentes'][1]['estado_durante']['aceptacion_automatica_demo'],False)

    def test_cooldown_evidencia(self):
        n=self.e['antirruido']
        self.assertEqual([n['primera_emision'],n['segunda_emision_2min'],n['emision_31min']],[1,0,1])

    def test_metrica_predictiva_y_alertas(self):
        b,d=demo_pares()
        base=evaluar_pares(b);degraded=evaluar_pares(d)
        self.assertGreater(base['accuracy'],degraded['accuracy'])
        self.assertTrue(alerta_calidad(base,degraded))
        self.assertEqual(sum(x['soporte'] for x in base['por_clase'].values()),32)

    def test_consola_clara(self):
        out=consola(self.e)
        self.assertIn('CONTROL ANTIRRUIDO',out)
        self.assertIn('RUNBOOK',out.upper())
        self.assertIn('[ALERTA',out)
        self.assertIn('ETIQUETAS FICTICIAS',out)

if __name__=='__main__':unittest.main()
