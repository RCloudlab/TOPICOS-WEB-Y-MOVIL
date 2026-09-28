import json
import re
from dataclasses import dataclass


@dataclass
class Sugerencia:
    medio: str
    motivo: str


class RecomendadorIA:
    def sugerir(self, pedido, contexto):
        raise NotImplementedError


MAPA_NOMBRES = {
    "bike": "bicicleta",
    "drone": "dron",
    "motorcycle": "moto",
    "van": "camioneta",
}


class ProveedorIAJson:
    def _llamar_proveedor(self, pedido, contexto):
        return json.dumps({"route_hint": "bike", "score": 0.9, "reason_code": "FASTEST"})


class AdaptadorProveedorIAJson(RecomendadorIA):
    def __init__(self, proveedor=None):
        self.proveedor = proveedor or ProveedorIAJson()

    def sugerir(self, pedido, contexto):
        crudo = json.loads(self.proveedor._llamar_proveedor(pedido, contexto))
        medio = MAPA_NOMBRES.get(crudo["route_hint"], crudo["route_hint"])
        motivo = f"IA (json): {crudo['reason_code']} (score={crudo['score']})"
        return Sugerencia(medio=medio, motivo=motivo)


class ProveedorIAXml:
    def _llamar_proveedor(self, pedido, contexto):
        return "<sugerencia><vehicle>drone</vehicle><reason>WEATHER_OK</reason></sugerencia>"


class AdaptadorProveedorIAXml(RecomendadorIA):
    def __init__(self, proveedor=None):
        self.proveedor = proveedor or ProveedorIAXml()

    def sugerir(self, pedido, contexto):
        crudo = self.proveedor._llamar_proveedor(pedido, contexto)
        vehiculo = re.search(r"<vehicle>(.*?)</vehicle>", crudo).group(1)
        razon = re.search(r"<reason>(.*?)</reason>", crudo)
        medio = MAPA_NOMBRES.get(vehiculo, vehiculo)
        motivo = f"IA (xml): {razon.group(1) if razon else 'SIN_RAZON'}"
        return Sugerencia(medio=medio, motivo=motivo)
