from entregas.models import Pedido


def registrar_pedido(origen, destino, peso_kg):
    return Pedido.objects.create(
        origen=origen,
        destino=destino,
        peso_kg=peso_kg,
    )
