from entregas.dominio.medios import (
    EntregaBicicleta,
    EntregaCamioneta,
    EntregaDron,
    EntregaMotocicleta,
)

MEDIOS = {
    "camioneta": EntregaCamioneta,
    "moto": EntregaMotocicleta,
    "bicicleta": EntregaBicicleta,
    "dron": EntregaDron,
}


def crear(tipo):
    clase = MEDIOS.get(tipo)
    if clase is None:
        raise ValueError(f"No existe el medio de entrega '{tipo}'")
    return clase()
