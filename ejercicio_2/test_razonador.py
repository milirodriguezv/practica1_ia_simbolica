"""
Tests del razonador.

Uso:
    python -m unittest test_razonador.py -v
"""

import copy
import unittest

import razonador
from carta import CARTA
from ontologia import ONTOLOGIA


class TestRazonador(unittest.TestCase):

    def test_ontologia_valida(self):
        self.assertEqual(razonador.validar_ontologia(ONTOLOGIA, CARTA), [])

    def test_ancestros_de_la_mozzarella(self):
        self.assertEqual(razonador.ancestros("Mozzarella", ONTOLOGIA),
                         {"Mozzarella", "Lacteo", "IngAnimal", "ConLactosa", "Ingrediente"})

    def test_ingrediente_desconocido(self):
        """Un plato con un ingrediente que no esta en la ontologia."""
        carta = copy.deepcopy(CARTA)
        carta["platos"]["PlatoRaro"] = {"tipo": "Principal",
                                        "componentes": ["Unicornio"],
                                        "etiquetas_carta": []}
        errores = razonador.validar_ontologia(ONTOLOGIA, carta)
        self.assertTrue(any("Unicornio" in e for e in errores))

    def test_clasificacion_de_la_carbonara(self):
        """Lleva pasta, guanciale, huevo y pecorino: no cumple nada."""
        inferidas, _ = razonador.clasificar("PastaCarbonara", ONTOLOGIA, CARTA)
        self.assertEqual(inferidas, [])

    def test_clasificacion_de_los_espaguetis(self):
        inferidas, _ = razonador.clasificar("EspaguetisAlPomodoro", ONTOLOGIA, CARTA)
        self.assertEqual(set(inferidas), {"Vegetariano", "SinCarne", "SinLactosa", "Vegano"})

    def test_la_lactosa_del_helado_esta_en_la_base(self):
        """La justificacion debe decir por donde se llega a la leche."""
        _, motivos = razonador.clasificar("HeladoDePistacho", ONTOLOGIA, CARTA)
        ingredientes = [v["ingrediente"] for v in motivos["SinLactosa"]]
        self.assertEqual(sorted(ingredientes), ["Leche", "Nata"])
        self.assertEqual(motivos["SinLactosa"][0]["ruta"], ["HeladoDePistacho", "BaseHelado"])

    def test_vegetariano_implica_sincarne_pero_no_al_reves(self):
        ok, _ = razonador.subsume("Vegetariano", "SinCarne", ONTOLOGIA)
        self.assertTrue(ok)
        ok, contraejemplo = razonador.subsume("SinCarne", "Vegetariano", ONTOLOGIA)
        self.assertFalse(ok)
        # el contraejemplo tiene que ser un pescado
        self.assertIn("Pescado", razonador.ancestros(contraejemplo, ONTOLOGIA))

    def test_vegetariano_con_pescado_es_imposible(self):
        ok, _ = razonador.es_satisfacible(["Vegetariano"], ["Pescado"], ONTOLOGIA)
        self.assertFalse(ok)

    def test_sinlactosa_con_lacteo_es_posible_con_parmesano(self):
        ok, testigo = razonador.es_satisfacible(["SinLactosa"], ["Lacteo"], ONTOLOGIA)
        self.assertTrue(ok)
        self.assertEqual(testigo, ["Parmesano"])

    def test_auditoria_detecta_la_etiqueta_falsa_del_helado(self):
        discrepancias = razonador.auditar_carta(ONTOLOGIA, CARTA)
        falsas = [(d["plato"], d["categoria"]) for d in discrepancias
                  if d["tipo"] == "ETIQUETA FALSA"]
        self.assertEqual(falsas, [("HeladoDePistacho", "SinLactosa")])


if __name__ == "__main__":
    unittest.main()
