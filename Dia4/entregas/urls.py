from django.urls import path

from entregas import views

urlpatterns = [
    path("pedidos/nuevo", views.nuevo_pedido, name="nuevo_pedido"),
    path("pedidos", views.crear_pedido, name="crear_pedido"),
    path("pedidos/<int:pedido_id>", views.seguimiento_pedido, name="seguimiento_pedido"),
    path("reporte", views.reporte_pedidos, name="reporte_pedidos"),
]
