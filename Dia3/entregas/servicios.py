from entregas.dominio.fabrica import crear
from entregas.dominio.ia import AdaptadorProveedorIAJson
from entregas.models import Pedido

RECOMENDADOR_POR_DEFECTO = AdaptadorProveedorIAJson()
MEDIO_DE_RESPALDO = "camioneta"


def registrar_pedido(origen, destino, peso_kg, contexto, recomendador=None):
    recomendador = recomendador or RECOMENDADOR_POR_DEFECTO

    pedido = Pedido(origen=origen, destino=destino, peso_kg=peso_kg)

    sugerencia = recomendador.sugerir(pedido, contexto)
    medio = crear(sugerencia.medio)
    plan = medio.planear(pedido, contexto)
    motivo = sugerencia.motivo

    if not plan.aplica:
        motivo = f"{sugerencia.motivo}; sin aplicar ({sugerencia.medio}), se usó respaldo"
        medio = crear(MEDIO_DE_RESPALDO)
        plan = medio.planear(pedido, contexto)

    pedido.medio = plan.medio
    pedido.motivo = motivo
    pedido.save()

    return pedido
