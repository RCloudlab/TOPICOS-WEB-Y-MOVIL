from django.db import models


class Pedido(models.Model):
    origen = models.CharField(max_length=200)
    destino = models.CharField(max_length=200)
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2)
    estado = models.CharField(max_length=50, default="CREADO")
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} ({self.estado})"
