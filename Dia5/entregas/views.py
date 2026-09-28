import uuid

from django.http import Http404, HttpResponseNotAllowed, JsonResponse
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import render
from django.urls import reverse

from entregas.dominio.medios import ContextoViaje
from entregas.models import Pedido
from entregas.servicios import consultar_inicio, consultar_seguimiento, registrar_pedido


class HttpResponseSeeOther(HttpResponseRedirectBase):
    status_code = 303


def nuevo_pedido(request):
    return render(request, "entregas/nuevo_pedido.html", {"clave_intento": uuid.uuid4()})


def crear_pedido(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    origen = request.POST.get("origen", "")
    destino = request.POST.get("destino", "")
    peso_kg = request.POST.get("peso_kg", "")
    clave_idempotencia = request.POST.get("clave_intento", "")

    contexto = ContextoViaje(distancia_km=5, viento_alto=False)
    pedido = registrar_pedido(origen, destino, peso_kg, contexto, clave_idempotencia)

    url = reverse("seguimiento_pedido", kwargs={"pedido_id": pedido.id})
    return HttpResponseSeeOther(url)


def seguimiento_pedido(request, pedido_id):
    datos = consultar_seguimiento(pedido_id)
    if datos is None:
        raise Http404("Pedido no encontrado")
    return render(request, "entregas/seguimiento.html", datos)


def reporte_pedidos(request):
    folios = Pedido.objects.values_list("id", flat=True).order_by("id")
    pedidos = [consultar_seguimiento(folio) for folio in folios]
    return render(request, "entregas/reporte.html", {"pedidos": pedidos})


def api_pedido(request, pedido_id):
    datos = consultar_seguimiento(pedido_id)
    if datos is None:
        return JsonResponse({"error": "Pedido no encontrado"}, status=404)

    return JsonResponse({
        "folio": datos["folio"],
        "estado": datos["estado"],
        "eta": datos["eta"],
    })


def api_inicio(request):
    return JsonResponse({"pedidos": consultar_inicio()})
