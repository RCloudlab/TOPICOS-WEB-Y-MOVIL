from django.db import models


class Pedido(models.Model):
    origen = models.CharField(max_length=200)
    destino = models.CharField(max_length=200)
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2)
    estado = models.CharField(max_length=50, default="CREADO")
    medio = models.CharField(max_length=50, blank=True, default="")
    motivo = models.CharField(max_length=200, blank=True, default="")
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} ({self.estado})"


class Cobro(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="cobros")
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    clave_idempotencia = models.CharField(max_length=64, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cobro #{self.id} (pedido {self.pedido_id})"
