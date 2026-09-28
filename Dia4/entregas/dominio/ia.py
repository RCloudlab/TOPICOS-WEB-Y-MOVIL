import json
import re
import time
from dataclasses import dataclass


@dataclass
class Sugerencia:
    medio: str
    motivo: str


class ErrorTemporalIA(Exception):
    """La IA tardó de más o falló de forma transitoria: vale la pena reintentar."""


class ErrorValidacionIA(Exception):
    """La IA respondió algo que no se puede interpretar: no tiene caso reintentar."""


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
    def __init__(self, tardanza_segundos=0, lanzar_error=False):
        self.tardanza_segundos = tardanza_segundos
        self.lanzar_error = lanzar_error

    def _llamar_proveedor(self, pedido, contexto):
        if self.tardanza_segundos:
            time.sleep(self.tardanza_segundos)
        if self.lanzar_error:
            raise ErrorTemporalIA("el proveedor de IA falló")
        return json.dumps({"route_hint": "bike", "score": 0.9, "reason_code": "FASTEST"})


class AdaptadorProveedorIAJson(RecomendadorIA):
    def __init__(self, proveedor=None):
        self.proveedor = proveedor or ProveedorIAJson()

    def sugerir(self, pedido, contexto):
        crudo_texto = self.proveedor._llamar_proveedor(pedido, contexto)
        try:
            crudo = json.loads(crudo_texto)
            medio = MAPA_NOMBRES.get(crudo["route_hint"], crudo["route_hint"])
            motivo = f"IA (json): {crudo['reason_code']} (score={crudo['score']})"
        except (json.JSONDecodeError, KeyError) as exc:
            raise ErrorValidacionIA(f"respuesta de IA (json) inválida: {exc}") from exc
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
