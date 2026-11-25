from abc import ABC, abstractmethod


class MedioDeEntrega(ABC):
    @abstractmethod
    def planear(self, paquete: dict) -> dict:
        pass


class EntregaBicicleta(MedioDeEntrega):
    def planear(self, paquete):
        minutos = paquete["distancia_km"] / 15 * 60
        return {
            "medio": "bicicleta",
            "minutos": round(minutos),
            "indicacion": "ruta por ciclovías",
        }


class EntregaMotocicleta(MedioDeEntrega):
    def planear(self, paquete):
        minutos = paquete["distancia_km"] / 35 * 60
        return {
            "medio": "moto",
            "minutos": round(minutos),
            "indicacion": "ruta por avenidas",
        }


class EntregaCamioneta(MedioDeEntrega):
    def planear(self, paquete):
        minutos = paquete["distancia_km"] / 30 * 60
        indicacion = (
            "unidad refrigerada" if paquete["refrigerado"] else "ruta de reparto"
        )
        return {
            "medio": "camioneta",
            "minutos": round(minutos),
            "indicacion": indicacion,
        }


class EntregaDron(MedioDeEntrega):
    def planear(self, paquete):
        minutos = paquete["distancia_km"] * 0.75 / 70 * 60
        return {
            "medio": "dron",
            "minutos": round(minutos),
            "indicacion": "vuelo en línea recta",
        }


MEDIOS = {
    "bicicleta": EntregaBicicleta,
    "moto": EntregaMotocicleta,
    "camioneta": EntregaCamioneta,
    "dron": EntregaDron,
}


def crear_medio(nombre: str) -> MedioDeEntrega:
    return MEDIOS[nombre]()
