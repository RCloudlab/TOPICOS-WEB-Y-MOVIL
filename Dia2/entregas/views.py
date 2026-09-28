from django.http import HttpResponseNotAllowed
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from entregas.models import Pedido
from entregas.servicios import registrar_pedido


class HttpResponseSeeOther(HttpResponseRedirectBase):
    status_code = 303


def nuevo_pedido(request):
    return render(request, "entregas/nuevo_pedido.html")


def crear_pedido(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    origen = request.POST.get("origen", "")
    destino = request.POST.get("destino", "")
    peso_kg = request.POST.get("peso_kg", "")

    pedido = registrar_pedido(origen, destino, peso_kg)

    url = reverse("seguimiento_pedido", kwargs={"pedido_id": pedido.id})
    return HttpResponseSeeOther(url)


def seguimiento_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    contexto = {
        "folio": pedido.id,
        "estado": pedido.estado,
        "eta": "30 min",
    }
    return render(request, "entregas/seguimiento.html", contexto)
