from django.test import TestCase

from entregas.dominio.fabrica import crear
from entregas.dominio.ia import (
    AdaptadorProveedorIAJson,
    AdaptadorProveedorIAXml,
    RecomendadorIA,
    Sugerencia,
)
from entregas.dominio.medios import (
    ContextoViaje,
    EntregaBicicleta,
    EntregaCamioneta,
    EntregaDron,
    EntregaMotocicleta,
)
from entregas.servicios import registrar_pedido


class PedidoFalso:
    def __init__(self, peso_kg):
        self.peso_kg = peso_kg


class MediosTests(TestCase):
    def test_camioneta_aplica_con_peso_grande(self):
        plan = EntregaCamioneta().planear(PedidoFalso(500), ContextoViaje(distancia_km=20))
        self.assertTrue(plan.aplica)
        self.assertEqual(plan.medio, "camioneta")

    def test_camioneta_siempre_aplica(self):
        plan = EntregaCamioneta().planear(PedidoFalso(1), ContextoViaje(distancia_km=1))
        self.assertTrue(plan.aplica)

    def test_moto_aplica_con_peso_medio(self):
        plan = EntregaMotocicleta().planear(PedidoFalso(10), ContextoViaje(distancia_km=8))
        self.assertTrue(plan.aplica)
        self.assertEqual(plan.medio, "moto")

    def test_moto_no_aplica_con_peso_excesivo(self):
        plan = EntregaMotocicleta().planear(PedidoFalso(20), ContextoViaje(distancia_km=8))
        self.assertFalse(plan.aplica)

    def test_bicicleta_aplica_con_paquete_chico_y_distancia_corta(self):
        plan = EntregaBicicleta().planear(PedidoFalso(2), ContextoViaje(distancia_km=3))
        self.assertTrue(plan.aplica)
        self.assertEqual(plan.medio, "bicicleta")

    def test_bicicleta_no_aplica_con_distancia_larga(self):
        plan = EntregaBicicleta().planear(PedidoFalso(2), ContextoViaje(distancia_km=10))
        self.assertFalse(plan.aplica)

    def test_dron_aplica_con_peso_chico_y_sin_viento(self):
        plan = EntregaDron().planear(PedidoFalso(1), ContextoViaje(distancia_km=4, viento_alto=False))
        self.assertTrue(plan.aplica)
        self.assertEqual(plan.medio, "dron")

    def test_dron_no_aplica_con_peso_excesivo(self):
        plan = EntregaDron().planear(PedidoFalso(10), ContextoViaje(distancia_km=4))
        self.assertFalse(plan.aplica)

    def test_dron_no_aplica_con_viento_alto(self):
        plan = EntregaDron().planear(PedidoFalso(1), ContextoViaje(distancia_km=4, viento_alto=True))
        self.assertFalse(plan.aplica)


class AdaptadoresIATests(TestCase):
    def test_adaptador_json_traduce_a_sugerencia(self):
        sugerencia = AdaptadorProveedorIAJson().sugerir(PedidoFalso(1), ContextoViaje(distancia_km=1))
        self.assertIsInstance(sugerencia, Sugerencia)
        self.assertEqual(sugerencia.medio, "bicicleta")

    def test_adaptador_xml_traduce_a_sugerencia(self):
        sugerencia = AdaptadorProveedorIAXml().sugerir(PedidoFalso(1), ContextoViaje(distancia_km=1))
        self.assertIsInstance(sugerencia, Sugerencia)
        self.assertEqual(sugerencia.medio, "dron")

    def test_json_y_xml_devuelven_el_mismo_tipo_de_sugerencia(self):
        json_sug = AdaptadorProveedorIAJson().sugerir(PedidoFalso(1), ContextoViaje(distancia_km=1))
        xml_sug = AdaptadorProveedorIAXml().sugerir(PedidoFalso(1), ContextoViaje(distancia_km=1))
        for sug in (json_sug, xml_sug):
            self.assertTrue(hasattr(sug, "medio"))
            self.assertTrue(hasattr(sug, "motivo"))


class FabricaTests(TestCase):
    def test_crear_devuelve_el_medio_correcto(self):
        self.assertIsInstance(crear("dron"), EntregaDron)
        self.assertIsInstance(crear("moto"), EntregaMotocicleta)
        self.assertIsInstance(crear("bicicleta"), EntregaBicicleta)
        self.assertIsInstance(crear("camioneta"), EntregaCamioneta)

    def test_crear_lanza_error_con_tipo_invalido(self):
        with self.assertRaises(ValueError):
            crear("teletransportador")


class RecomendadorDronFalso(RecomendadorIA):
    def sugerir(self, pedido, contexto):
        return Sugerencia(medio="dron", motivo="IA (falsa): sugiere dron")


class RegistrarPedidoTests(TestCase):
    def test_usa_respaldo_cuando_el_medio_sugerido_no_aplica(self):
        contexto = ContextoViaje(distancia_km=4, viento_alto=False)
        pedido = registrar_pedido(
            "CDMX", "Toluca", "10", contexto, recomendador=RecomendadorDronFalso()
        )
        self.assertEqual(pedido.medio, "camioneta")
        self.assertIn("sin aplicar", pedido.motivo)
        self.assertIn("dron", pedido.motivo)

    def test_no_duplica_pedidos_al_registrar(self):
        contexto = ContextoViaje(distancia_km=4)
        registrar_pedido("A", "B", "1", contexto, recomendador=RecomendadorDronFalso())
        from entregas.models import Pedido

        self.assertEqual(Pedido.objects.count(), 1)
