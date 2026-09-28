"""
Tests del razonador.

Uso:
    python -m unittest test_razonador.py -v

Las variantes de la ontologia o de la carta se hacen sobre copias
(copy.deepcopy), asi que ONTOLOGIA y CARTA nunca se modifican.
"""

import copy
import unittest

import razonador
from carta import CARTA
from ontologia import ONTOLOGIA

# Clasificacion esperada de cada plato (tabla de E1)
CLASIFICACION_ESPERADA = {
    "VitelTone": {"SinGluten", "SinLactosa"},
    "BurrataConTomatesConfitados": {"SinGluten", "Vegetariano", "SinCarne"},
    "PizzaMozzarella": {"Vegetariano", "SinCarne"},
    "PastaCarbonara": set(),
    "EnsaladaRuculaPeraParmesano": {"SinGluten", "Vegetariano", "SinCarne", "SinLactosa"},
    "SalmonConVerdurasAlHorno": {"SinGluten", "SinCarne", "SinLactosa"},
    "Tiramisu": {"Vegetariano", "SinCarne"},
    "HeladoDePistacho": {"SinGluten", "Vegetariano", "SinCarne"},
}


def carta_con_plato(nombre, componentes, etiquetas=None):
    """Copia de la carta con un plato extra."""
    carta = copy.deepcopy(CARTA)
    carta["platos"][nombre] = {"tipo": "Principal",
                               "componentes": componentes,
                               "etiquetas_carta": etiquetas or []}
    return carta


class TestOntologia(unittest.TestCase):

    def test_ontologia_valida(self):
        self.assertEqual(razonador.validar_ontologia(ONTOLOGIA, CARTA), [])

    def test_ancestros_con_herencia_multiple(self):
        self.assertEqual(razonador.ancestros("Mozzarella", ONTOLOGIA),
                         {"Mozzarella", "Lacteo", "IngAnimal", "ConLactosa", "Ingrediente"})

    def test_detecta_clases_disjuntas(self):
        onto = copy.deepcopy(ONTOLOGIA)
        onto["taxonomia"]["Tomate"] = ["Verdura", "Carne"]  # animal y no animal
        errores = razonador.validar_ontologia(onto, CARTA)
        self.assertTrue(any("disjuntas" in e and "Tomate" in e for e in errores))

    def test_detecta_ingrediente_desconocido(self):
        carta = carta_con_plato("PlatoRaro", ["Unicornio"])
        errores = razonador.validar_ontologia(ONTOLOGIA, carta)
        self.assertTrue(any("Unicornio" in e for e in errores))


class TestClasificacion(unittest.TestCase):

    def test_clasificacion_de_cada_plato(self):
        for plato, esperadas in CLASIFICACION_ESPERADA.items():
            with self.subTest(plato=plato):
                inferidas, _ = razonador.clasificar(plato, ONTOLOGIA, CARTA)
                self.assertEqual(set(inferidas), esperadas)

    def test_justificacion_atraviesa_elaborados(self):
        """La lactosa del helado esta dentro de BaseHelado: la justificacion
        debe dar el ingrediente y la ruta por la que se llega a el."""
        _, motivos = razonador.clasificar("HeladoDePistacho", ONTOLOGIA, CARTA)
        ingredientes = {(v["ingrediente"], tuple(v["ruta"])) for v in motivos["SinLactosa"]}
        self.assertEqual(ingredientes, {("Leche", ("HeladoDePistacho", "BaseHelado")),
                                        ("Nata", ("HeladoDePistacho", "BaseHelado"))})

    def test_plato_vacio_no_pertenece_a_ninguna_categoria(self):
        """Sin PlatoValido, un plato vacio cumpliria todas las categorias
        por verdad vacia del ∀."""
        carta = carta_con_plato("PlatoVacio", [])
        inferidas, _ = razonador.clasificar("PlatoVacio", ONTOLOGIA, carta)
        self.assertEqual(inferidas, [])

    def test_ciclo_entre_elaborados(self):
        carta = carta_con_plato("PlatoCiclico", ["SalsaA"])
        carta["compuestos"]["SalsaA"] = ["Tomate", "SalsaB"]
        carta["compuestos"]["SalsaB"] = ["Ajo", "SalsaA"]
        with self.assertRaises(ValueError):
            razonador.ingredientes_de_plato("PlatoCiclico", carta)
        errores = razonador.validar_ontologia(ONTOLOGIA, carta)
        self.assertTrue(any("Ciclo" in e for e in errores))


class TestSubsuncion(unittest.TestCase):

    def test_vegetariano_subsume_a_sincarne(self):
        ok, contraejemplo = razonador.subsume("Vegetariano", "SinCarne", ONTOLOGIA)
        self.assertTrue(ok)
        self.assertIsNone(contraejemplo)

    def test_sincarne_no_subsume_a_vegetariano(self):
        ok, contraejemplo = razonador.subsume("SinCarne", "Vegetariano", ONTOLOGIA)
        self.assertFalse(ok)
        # El contraejemplo es un pescado: cumple SinCarne pero no Vegetariano
        self.assertIn("Pescado", razonador.ancestros(contraejemplo, ONTOLOGIA))

    def test_unica_subsuncion_inferida(self):
        positivas = {(r["c"], r["d"]) for r in razonador.jerarquia_categorias(ONTOLOGIA)
                     if r["subsume"]}
        self.assertEqual(positivas, {("Vegetariano", "SinCarne")})

    def test_contraejemplos_son_correctos(self):
        """Cada contraejemplo {h} cumple C y no cumple D."""
        for r in razonador.jerarquia_categorias(ONTOLOGIA):
            if r["subsume"]:
                continue
            with self.subTest(c=r["c"], d=r["d"]):
                carta = carta_con_plato("Contraejemplo", [r["contraejemplo"]])
                inferidas, _ = razonador.clasificar("Contraejemplo", ONTOLOGIA, carta)
                self.assertIn(r["c"], inferidas)
                self.assertNotIn(r["d"], inferidas)


class TestConsistencia(unittest.TestCase):

    def test_vegetariano_con_pescado_es_insatisfacible(self):
        ok, _ = razonador.es_satisfacible(["Vegetariano"], ["Pescado"], ONTOLOGIA)
        self.assertFalse(ok)

    def test_sinlactosa_con_lacteo_es_satisfacible(self):
        ok, testigo = razonador.es_satisfacible(["SinLactosa"], ["Lacteo"], ONTOLOGIA)
        self.assertTrue(ok)
        self.assertEqual(testigo, ["Parmesano"])


class TestAuditoria(unittest.TestCase):

    def test_detecta_la_etiqueta_falsa_del_helado(self):
        discrepancias = razonador.auditar_carta(ONTOLOGIA, CARTA)
        falsas = [(d["plato"], d["categoria"]) for d in discrepancias
                  if d["tipo"] == "ETIQUETA FALSA"]
        self.assertEqual(falsas, [("HeladoDePistacho", "SinLactosa")])

    def test_omision_no_se_repite_si_la_implica_otra(self):
        """Un plato Vegetariano no debe avisar de que tambien es SinCarne."""
        discrepancias = razonador.auditar_carta(ONTOLOGIA, CARTA)
        omisiones = {(d["plato"], d["categoria"]) for d in discrepancias
                     if d["tipo"] == "OMISION"}
        self.assertNotIn(("EnsaladaRuculaPeraParmesano", "SinCarne"), omisiones)
        self.assertIn(("SalmonConVerdurasAlHorno", "SinCarne"), omisiones)


if __name__ == "__main__":
    unittest.main()
