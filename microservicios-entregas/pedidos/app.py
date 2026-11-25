"""Servicio pedidos: registra el pedido y le pide el medio a recomendar por red.

No tiene scikit-learn. Si recomendar no responde, el pedido se guarda igual
como "pendiente_de_medio" y se avisa; nunca se inventa un medio.
"""
import itertools
import os
import threading
from datetime import datetime

import requests
from flask import Flask, jsonify, request

from medios import crear_medio

RECOMENDAR_URL = os.environ.get("RECOMENDAR_URL", "http://recomendar:5001")
TIMEOUT_S = float(os.environ.get("RECOMENDAR_TIMEOUT", "3"))

app = Flask(__name__)
_pedidos = {}            # en memoria: suficiente para la actividad (ver límites en el reporte)
_contador = itertools.count(1)
_candado = threading.Lock()


def _nuevo_folio():
    with _candado:
        return f"PED-{next(_contador):05d}"


@app.get("/salud")
def salud():
    return jsonify({"servicio": "pedidos", "ok": True, "recomendar_url": RECOMENDAR_URL})


@app.post("/pedidos")
def crear_pedido():
    paquete = request.get_json(silent=True)
    if not isinstance(paquete, dict):
        return jsonify({"error": "el cuerpo debe ser JSON"}), 400

    folio = _nuevo_folio()
    pedido = {"folio": folio, "creado": datetime.now().isoformat(timespec="seconds"), "paquete": paquete}

    try:
        r = requests.post(f"{RECOMENDAR_URL}/sugerir", json=paquete, timeout=TIMEOUT_S)
    except requests.RequestException as error:
        pedido.update(estado="pendiente_de_medio", medio=None,
                      aviso=f"recomendar no disponible ({type(error).__name__}); el pedido quedó registrado sin medio")
        _pedidos[folio] = pedido
        return jsonify(pedido), 202

    if r.status_code == 400:
        return jsonify({"error": "paquete inválido", "detalle": r.json()}), 400
    if r.status_code != 200:
        pedido.update(estado="pendiente_de_medio", medio=None,
                      aviso=f"recomendar respondió {r.status_code}; el pedido quedó registrado sin medio")
        _pedidos[folio] = pedido
        return jsonify(pedido), 202

    sugerencia = r.json()
    numeros = {k: float(v) for k, v in paquete.items() if k in ("distancia_km", "refrigerado")}
    pedido.update(
        estado="registrado",
        medio=sugerencia["medio"],
        motivo=sugerencia["motivo"],
        modelo=sugerencia["modelo"],
        ranking=sugerencia["ranking"],
        descartados=sugerencia["descartados"],
        corregido_por_reglas=sugerencia["corregido_por_reglas"],
        plan=crear_medio(sugerencia["medio"]).planear(numeros),
    )
    _pedidos[folio] = pedido
    return jsonify(pedido), 201


@app.get("/pedidos/<folio>")
def ver_pedido(folio):
    pedido = _pedidos.get(folio)
    if pedido is None:
        return jsonify({"error": "folio no encontrado"}), 404
    return jsonify(pedido)
