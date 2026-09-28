import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturoTimeoutError

from django.conf import settings
from django.db import transaction

from entregas.dominio.fabrica import crear
from entregas.dominio.ia import AdaptadorProveedorIAJson, ErrorValidacionIA, ErrorTemporalIA
from entregas.models import Cobro, Pedido

logger = logging.getLogger(__name__)

RECOMENDADOR_POR_DEFECTO = AdaptadorProveedorIAJson()
MEDIO_DE_RESPALDO = "camioneta"
MOTIVO_IA_NO_DISPONIBLE = "IA no disponible"
MAXIMO_REINTENTOS_IA = 1


def _pedir_sugerencia_con_timeout(recomendador, pedido, contexto, timeout_segundos):
    intentos = 0
    while True:
        intentos += 1
        pool = ThreadPoolExecutor(max_workers=1)
        futuro = pool.submit(recomendador.sugerir, pedido, contexto)
        try:
            resultado = futuro.result(timeout=timeout_segundos)
            pool.shutdown(wait=False)
            return resultado
        except FuturoTimeoutError as exc:
            error = exc
        except ErrorTemporalIA as exc:
            error = exc
        except ErrorValidacionIA:
            pool.shutdown(wait=False)
            raise
        pool.shutdown(wait=False)

        if intentos > MAXIMO_REINTENTOS_IA:
            raise error


def _elegir_medio(pedido, contexto, recomendador):
    if not settings.IA_ACTIVA:
        return MEDIO_DE_RESPALDO, MOTIVO_IA_NO_DISPONIBLE

    try:
        sugerencia = _pedir_sugerencia_con_timeout(
            recomendador, pedido, contexto, settings.IA_TIMEOUT_SEGUNDOS
        )
    except (FuturoTimeoutError, ErrorTemporalIA, ErrorValidacionIA):
        return MEDIO_DE_RESPALDO, MOTIVO_IA_NO_DISPONIBLE

    medio = crear(sugerencia.medio)
    plan = medio.planear(pedido, contexto)
    if not plan.aplica:
        motivo = f"{sugerencia.motivo}; sin aplicar ({sugerencia.medio}), se usó respaldo"
        return MEDIO_DE_RESPALDO, motivo

    return sugerencia.medio, sugerencia.motivo


def realizar_cobro(pedido, clave_idempotencia):
    return Cobro.objects.create(
        pedido=pedido,
        monto=50 + float(pedido.peso_kg) * 2,
        clave_idempotencia=clave_idempotencia,
    )


def _avisar(pedido):
    if settings.AVISO_FALLA_A_PROPOSITO:
        raise RuntimeError("aviso simulado que falla a propósito")
    print(f"[aviso] pedido #{pedido.id} registrado, medio={pedido.medio}")


def _avisar_sin_tumbar_la_respuesta(pedido_id):
    def avisar():
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            _avisar(pedido)
        except Exception:
            logger.exception("Falló el aviso del pedido #%s", pedido_id)

    return avisar


def registrar_pedido(origen, destino, peso_kg, contexto, clave_idempotencia, recomendador=None):
    recomendador = recomendador or RECOMENDADOR_POR_DEFECTO

    cobro_existente = Cobro.objects.filter(clave_idempotencia=clave_idempotencia).select_related("pedido").first()
    if cobro_existente is not None:
        return cobro_existente.pedido

    pedido_temporal = Pedido(origen=origen, destino=destino, peso_kg=peso_kg)
    medio, motivo = _elegir_medio(pedido_temporal, contexto, recomendador)

    with transaction.atomic():
        pedido = Pedido.objects.create(
            origen=origen,
            destino=destino,
            peso_kg=peso_kg,
            medio=medio,
            motivo=motivo,
        )
        realizar_cobro(pedido, clave_idempotencia)
        transaction.on_commit(_avisar_sin_tumbar_la_respuesta(pedido.id))

    return pedido


def consultar_seguimiento(folio):
    pedido = Pedido.objects.filter(id=folio).first()
    if pedido is None:
        return None

    return {
        "folio": pedido.id,
        "estado": pedido.estado,
        "medio": pedido.medio,
        "motivo": pedido.motivo,
        "eta": "30 min",
        "lat": 19.4326,
        "lng": -99.1332,
    }
