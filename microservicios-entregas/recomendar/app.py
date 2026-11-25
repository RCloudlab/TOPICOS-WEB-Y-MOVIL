"""Servicio recomendar: carga el modelo + reglas y sugiere un medio. No crea folios."""
from flask import Flask, jsonify, request

from ia.recomendador import CAMPOS, CAMPOS_NUMERICOS, MODELOS, modelos_disponibles, obtener_recomendador

app = Flask(__name__)


@app.get("/salud")
def salud():
    return jsonify({"servicio": "recomendar", "ok": True, "modelos": modelos_disponibles()})


@app.post("/sugerir")
def sugerir():
    paquete = request.get_json(silent=True)
    if not isinstance(paquete, dict):
        return jsonify({"error": "el cuerpo debe ser JSON"}), 400

    clave = paquete.pop("modelo", "arbol") or "arbol"
    if clave not in MODELOS:
        return jsonify({"error": "modelo desconocido", "modelos": list(MODELOS)}), 400

    faltantes = [c for c in CAMPOS if c not in paquete]
    if faltantes:
        return jsonify({"error": "faltan campos", "campos": faltantes}), 400
    try:
        for c in CAMPOS_NUMERICOS:
            paquete[c] = float(paquete[c])
    except (TypeError, ValueError):
        return jsonify({"error": f"el campo {c} debe ser un número"}), 400

    try:
        resultado = obtener_recomendador(clave).explicar(paquete)
    except FileNotFoundError as error:
        return jsonify({"error": str(error)}), 503

    datos = resultado.a_dict()
    datos.pop("proceso", None)  # el detalle de pasos se queda adentro del servicio
    return jsonify(datos)
