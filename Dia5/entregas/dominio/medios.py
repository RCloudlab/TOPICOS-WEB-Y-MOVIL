from dataclasses import dataclass


@dataclass
class ContextoViaje:
    distancia_km: float
    viento_alto: bool = False


@dataclass
class Plan:
    medio: str
    minutos: int
    costo: float
    aplica: bool

    @staticmethod
    def no_aplica(medio):
        return Plan(medio=medio, minutos=0, costo=0.0, aplica=False)


class MedioDeEntrega:
    nombre = "medio"

    def planear(self, pedido, contexto):
        raise NotImplementedError


class EntregaCamioneta(MedioDeEntrega):
    nombre = "camioneta"

    def planear(self, pedido, contexto):
        minutos = 20 + int(contexto.distancia_km * 3)
        costo = 50 + float(pedido.peso_kg) * 2
        return Plan(medio=self.nombre, minutos=minutos, costo=costo, aplica=True)


class EntregaMotocicleta(MedioDeEntrega):
    nombre = "moto"

    def planear(self, pedido, contexto):
        if float(pedido.peso_kg) > 15:
            return Plan.no_aplica(self.nombre)
        minutos = 10 + int(contexto.distancia_km * 2)
        costo = 30 + float(pedido.peso_kg) * 1.5
        return Plan(medio=self.nombre, minutos=minutos, costo=costo, aplica=True)


class EntregaBicicleta(MedioDeEntrega):
    nombre = "bicicleta"

    def planear(self, pedido, contexto):
        if float(pedido.peso_kg) > 5 or contexto.distancia_km > 5:
            return Plan.no_aplica(self.nombre)
        minutos = 15 + int(contexto.distancia_km * 4)
        costo = 15 + float(pedido.peso_kg)
        return Plan(medio=self.nombre, minutos=minutos, costo=costo, aplica=True)


class EntregaDron(MedioDeEntrega):
    nombre = "dron"

    def planear(self, pedido, contexto):
        if float(pedido.peso_kg) > 2 or contexto.viento_alto:
            return Plan.no_aplica(self.nombre)
        minutos = 5 + int(contexto.distancia_km)
        costo = 40 + float(pedido.peso_kg) * 5
        return Plan(medio=self.nombre, minutos=minutos, costo=costo, aplica=True)


class EntregaTriciclo(MedioDeEntrega):
    nombre = "triciclo"

    def planear(self, pedido, contexto):
        if float(pedido.peso_kg) > 8 or contexto.distancia_km > 6:
            return Plan.no_aplica(self.nombre)
        minutos = 12 + int(contexto.distancia_km * 3)
        costo = 20 + float(pedido.peso_kg) * 1.2
        return Plan(medio=self.nombre, minutos=minutos, costo=costo, aplica=True)
