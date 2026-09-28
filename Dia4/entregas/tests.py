from unittest.mock import patch

from django.test import Client, TestCase, override_settings

from entregas.dominio.fabrica import crear
from entregas.dominio.ia import (
    AdaptadorProveedorIAJson,
    AdaptadorProveedorIAXml,
    ProveedorIAJson,
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
from entregas.models import Cobro, Pedido
from entregas.servicios import consultar_seguimiento, registrar_pedido


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
        with self.captureOnCommitCallbacks(execute=True):
            pedido = registrar_pedido(
                "CDMX", "Toluca", "10", contexto, "clave-respaldo-1",
                recomendador=RecomendadorDronFalso(),
            )
        self.assertEqual(pedido.medio, "camioneta")
        self.assertIn("sin aplicar", pedido.motivo)
        self.assertIn("dron", pedido.motivo)

    def test_no_duplica_pedidos_al_registrar(self):
        contexto = ContextoViaje(distancia_km=4)
        with self.captureOnCommitCallbacks(execute=True):
            registrar_pedido(
                "A", "B", "1", contexto, "clave-no-duplica",
                recomendador=RecomendadorDronFalso(),
            )
        self.assertEqual(Pedido.objects.count(), 1)


class SeguimientoSinConsultasExtraTests(TestCase):
    def setUp(self):
        contexto = ContextoViaje(distancia_km=4)
        with self.captureOnCommitCallbacks(execute=True):
            self.pedido = registrar_pedido(
                "CDMX", "Puebla", "3", contexto, "clave-seguimiento",
                recomendador=RecomendadorDronFalso(),
            )

    def test_plantilla_seguimiento_no_dispara_consultas_extra(self):
        client = Client()
        with self.assertNumQueries(1):
            respuesta = client.get(f"/pedidos/{self.pedido.id}")
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, str(self.pedido.id))

    def test_reporte_usa_consultar_seguimiento(self):
        with patch(
            "entregas.views.consultar_seguimiento", wraps=consultar_seguimiento
        ) as espia:
            client = Client()
            respuesta = client.get("/reporte")
            self.assertEqual(respuesta.status_code, 200)
            espia.assert_called_once_with(self.pedido.id)


class TransaccionYAvisoTests(TestCase):
    def test_si_el_aviso_falla_el_pedido_y_el_cobro_siguen_guardados(self):
        contexto = ContextoViaje(distancia_km=4)
        with override_settings(AVISO_FALLA_A_PROPOSITO=True):
            with self.assertLogs("entregas.servicios", level="ERROR"):
                with self.captureOnCommitCallbacks(execute=True):
                    pedido = registrar_pedido(
                        "A", "B", "2", contexto, "clave-aviso-falla",
                        recomendador=RecomendadorDronFalso(),
                    )

        self.assertTrue(Pedido.objects.filter(id=pedido.id).exists())
        self.assertTrue(Cobro.objects.filter(pedido=pedido).exists())

    def test_si_el_cobro_falla_no_queda_pedido(self):
        contexto = ContextoViaje(distancia_km=4)
        pedidos_antes = Pedido.objects.count()

        with patch("entregas.servicios.realizar_cobro", side_effect=RuntimeError("cobro caído")):
            with self.assertRaises(RuntimeError):
                registrar_pedido(
                    "A", "B", "2", contexto, "clave-cobro-falla",
                    recomendador=RecomendadorDronFalso(),
                )

        self.assertEqual(Pedido.objects.count(), pedidos_antes)
        self.assertFalse(Cobro.objects.filter(clave_idempotencia="clave-cobro-falla").exists())

    def test_misma_clave_no_crea_segundo_pedido_ni_segundo_cobro(self):
        contexto = ContextoViaje(distancia_km=4)
        with self.captureOnCommitCallbacks(execute=True):
            primero = registrar_pedido(
                "A", "B", "2", contexto, "clave-repetida",
                recomendador=RecomendadorDronFalso(),
            )
        with self.captureOnCommitCallbacks(execute=True):
            segundo = registrar_pedido(
                "A", "B", "2", contexto, "clave-repetida",
                recomendador=RecomendadorDronFalso(),
            )

        self.assertEqual(primero.id, segundo.id)
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(Cobro.objects.filter(clave_idempotencia="clave-repetida").count(), 1)


class IACaidaTests(TestCase):
    def test_con_ia_apagada_se_usa_camioneta_y_el_motivo_correcto(self):
        contexto = ContextoViaje(distancia_km=4)
        with override_settings(IA_ACTIVA=False):
            with self.captureOnCommitCallbacks(execute=True):
                pedido = registrar_pedido("A", "B", "2", contexto, "clave-ia-apagada")

        self.assertEqual(pedido.medio, "camioneta")
        self.assertEqual(pedido.motivo, "IA no disponible")

    def test_folio_ya_guardado_se_sigue_viendo_con_ia_apagada(self):
        contexto = ContextoViaje(distancia_km=4)
        with override_settings(IA_ACTIVA=False):
            with self.captureOnCommitCallbacks(execute=True):
                pedido = registrar_pedido("A", "B", "2", contexto, "clave-folio-viejo")

            client = Client()
            respuesta = client.get(f"/pedidos/{pedido.id}")
        self.assertEqual(respuesta.status_code, 200)

    def test_si_la_ia_tarda_mas_del_timeout_se_usa_camioneta(self):
        contexto = ContextoViaje(distancia_km=4)
        proveedor_lento = ProveedorIAJson(tardanza_segundos=1)
        recomendador = AdaptadorProveedorIAJson(proveedor=proveedor_lento)
        with override_settings(IA_TIMEOUT_SEGUNDOS=0.1):
            with self.captureOnCommitCallbacks(execute=True):
                pedido = registrar_pedido(
                    "A", "B", "2", contexto, "clave-ia-lenta", recomendador=recomendador
                )
        self.assertEqual(pedido.medio, "camioneta")
        self.assertEqual(pedido.motivo, "IA no disponible")

    def test_si_la_ia_falla_temporalmente_reintenta_y_luego_usa_camioneta(self):
        contexto = ContextoViaje(distancia_km=4)
        proveedor_caido = ProveedorIAJson(lanzar_error=True)
        recomendador = AdaptadorProveedorIAJson(proveedor=proveedor_caido)
        with patch.object(
            recomendador, "sugerir", wraps=recomendador.sugerir
        ) as espia_sugerir:
            with self.captureOnCommitCallbacks(execute=True):
                pedido = registrar_pedido(
                    "A", "B", "2", contexto, "clave-ia-caida", recomendador=recomendador
                )
        self.assertEqual(pedido.medio, "camioneta")
        self.assertEqual(pedido.motivo, "IA no disponible")
        self.assertEqual(espia_sugerir.call_count, 2)
