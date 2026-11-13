import unittest
from src.drift import population_stability_index

class TestDrift(unittest.TestCase):
    def test_same_zero(self):
        a={"INDIVIDUAL":25,"PAQUETE":25,"AMBIGUA":25,"FUERA_ALCANCE":25}
        self.assertAlmostEqual(population_stability_index(a,a),0)

    def test_shift_detected(self):
        a={"INDIVIDUAL":25,"PAQUETE":25,"AMBIGUA":25,"FUERA_ALCANCE":25}
        b={"INDIVIDUAL":1,"PAQUETE":2,"AMBIGUA":2,"FUERA_ALCANCE":95}
        self.assertGreater(population_stability_index(a,b),.25)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):population_stability_index({}, {"INDIVIDUAL":1})

if __name__=="__main__":unittest.main()
