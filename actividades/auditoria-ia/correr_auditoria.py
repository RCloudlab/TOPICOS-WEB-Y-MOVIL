"""
Auditoría de KitAte con IA libre y local (Ollama).

1) Arma paquete_contexto.md con los archivos clave del proyecto, quitando secretos.
2) Manda el mismo prompt + paquete a cada modelo y guarda la respuesta.

Uso:
    py correr_auditoria.py <ruta_a_KitAte> [modelo1 modelo2 ...]
    py correr_auditoria.py C:/Users/rodri/Music/Proyecto1 llama3.2 qwen2.5-coder:7b
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).parent
OLLAMA = "http://localhost:11434"

ARCHIVOS = [
    "backend/tienda/settings.py",
    "backend/tienda/urls.py",
    "backend/requirements.txt",
    "backend/catalogo/models.py",
    "backend/catalogo/repositories.py",
    "backend/catalogo/views.py",
    "backend/recomendador/validacion.py",
    "backend/recomendador/reglas.py",
    "backend/recomendador/recomendador.py",
    "backend/recomendador/servicio.py",
    "backend/recomendador/views.py",
    "backend/pedidos/models.py",
    "backend/pedidos/repositories.py",
    "backend/pedidos/servicios.py",
    "backend/pedidos/views.py",
    "backend/asistente/adaptador.py",
    "backend/asistente/servicio.py",
    "backend/asistente/views.py",
    "app_flutter/lib/config/app_config.dart",
    "app_flutter/lib/services/api_client.dart",
    "app_flutter/android/app/src/main/AndroidManifest.xml",
    ".gitignore",
]

# Cosas que nunca salen de la máquina aunque el modelo sea local.
SECRETOS = [
    (re.compile(r"(SECRET_KEY\s*=\s*)['\"].*?['\"]"), r"\1'<OMITIDO: secreto>'"),
]

LENGUAJE = {".py": "python", ".dart": "dart", ".xml": "xml", ".txt": "text"}

PROMPT = """Eres un auditor de software. Abajo está el código de KitAte: una tienda de artículos
deportivos con backend Django + SQLite y una app Flutter que consume JSON. Un modelo de
scikit-learn sugiere un nivel de actividad, unas reglas lo corrigen y se registra un pedido
con folio. También hay un asistente (chat) que clasifica intenciones.

Audita SOLO lo que aparece en el paquete. Busca problemas de seguridad, errores de lógica,
validación, manejo de errores y configuración para producción.

Responde en español con una lista numerada. Para cada hallazgo usa exactamente este formato:

N. Título corto
- Severidad: alta | media | baja
- Archivo: ruta/del/archivo (y línea o función si la sabes)
- Evidencia: el fragmento de código o configuración que lo muestra
- Riesgo: qué puede pasar
- Verificación de 5 minutos: cómo comprobarlo a mano

Da entre 5 y 10 hallazgos. No inventes archivos que no estén en el paquete. Si algo no lo
puedes confirmar con el código mostrado, dilo.

===== PAQUETE DE CONTEXTO =====
"""


def armar_paquete(raiz: Path) -> str:
    partes = ["# Paquete de contexto: KitAte\n",
              "Archivos clave del proyecto. Secretos reemplazados por <OMITIDO>.\n"]
    for rel in ARCHIVOS:
        ruta = raiz / rel
        if not ruta.exists():
            continue
        texto = ruta.read_text(encoding="utf-8")
        for patron, reemplazo in SECRETOS:
            texto = patron.sub(reemplazo, texto)
        lang = LENGUAJE.get(ruta.suffix, "")
        partes.append(f"\n## {rel}\n```{lang}\n{texto.rstrip()}\n```\n")
    return "".join(partes)


def preguntar(modelo: str, mensaje: str, salida: Path) -> dict:
    """Pide la respuesta en streaming y la va escribiendo en `salida`.

    num_predict pone un tope de tokens: en la primera corrida llama3.2 se quedó
    generando más de 20 minutos sin terminar.
    """
    cuerpo = json.dumps({
        "model": modelo,
        "prompt": mensaje,
        "stream": True,
        "options": {"num_ctx": 20480, "num_predict": 2500, "temperature": 0.2,
                    "repeat_penalty": 1.15},
    }).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=cuerpo,
                                 headers={"Content-Type": "application/json"})
    inicio = time.time()
    texto, final = [], {}
    with urllib.request.urlopen(req, timeout=1800) as r, salida.open("w", encoding="utf-8") as f:
        for linea in r:
            trozo = json.loads(linea)
            texto.append(trozo.get("response", ""))
            f.write(trozo.get("response", ""))
            f.flush()
            if trozo.get("done"):
                final = trozo
    final["response"] = "".join(texto)
    final["segundos"] = round(time.time() - inicio, 1)
    return final


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    raiz = Path(sys.argv[1])
    modelos = sys.argv[2:] or ["llama3.2", "qwen2.5-coder:7b"]

    paquete = armar_paquete(raiz)
    (AQUI / "paquete_contexto.md").write_text(paquete, encoding="utf-8")
    (AQUI / "prompt_auditoria.txt").write_text(PROMPT, encoding="utf-8")
    assert "django-insecure" not in paquete, "¡La SECRET_KEY se coló en el paquete!"
    print(f"Paquete: {len(paquete):,} caracteres, {len(ARCHIVOS)} archivos")

    for modelo in modelos:
        print(f"→ {modelo} ...", flush=True)
        nombre = re.sub(r"[^a-z0-9]+", "_", modelo.lower()).strip("_")
        datos = preguntar(modelo, PROMPT + paquete, AQUI / f"_parcial_{nombre}.txt")
        (AQUI / f"_parcial_{nombre}.txt").unlink(missing_ok=True)
        encabezado = (f"# Respuesta de `{modelo}` (Ollama, local)\n\n"
                      f"- Tokens de entrada: {datos.get('prompt_eval_count')}\n"
                      f"- Tokens de salida: {datos.get('eval_count')}"
                      f"{' (llegó al tope de 2500)' if datos.get('done_reason') == 'length' else ''}\n"
                      f"- Tiempo: {datos['segundos']} s\n\n---\n\n")
        (AQUI / f"respuesta_{nombre}.md").write_text(encabezado + datos["response"], encoding="utf-8")
        print(f"  listo en {datos['segundos']} s (entrada {datos.get('prompt_eval_count')} tokens)")


if __name__ == "__main__":
    main()
