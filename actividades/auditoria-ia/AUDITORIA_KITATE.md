# Auditar el proyecto con IA libre (sin costo)

**Nombre:** Rodrigo Vega Espinoza
**Matrícula:** 22121334
**Proyecto auditado:** KitAte (Proyectos 1 y 2), tienda de artículos deportivos con Django + SQLite + Flutter. Repo: `RCloudlab/KitAte`
**Fecha:** 24/11/2026

---

## 1. Herramientas

Todo corrió **en mi computadora** con Ollama 0.40.17 (RTX 3050 6 GB + 16 GB RAM). Nada del código salió a internet.

| IA | Modelo | Tipo | Dónde corre |
|---|---|---|---|
| A | `llama3.2` (3B) | General | Local (Ollama) |
| B | `qwen2.5-coder:7b` | De código | Local (Ollama) |

No usé `glm-5.1:cloud`, que también tengo instalado, porque corre en la nube y el código saldría de mi máquina.

**Prueba de que responde** (`prueba_ollama.txt`): le pedí a `llama3.2` "Responde solo: OK" y contestó "¿En qué puedo ayudarte hoy?". Responde, pero no sigue instrucciones al pie de la letra, y eso se volvió a ver en la auditoría.

---

## 2. Qué se mandó y qué se omitió

El script [`correr_auditoria.py`](correr_auditoria.py) arma el paquete y manda **el mismo prompt** ([`prompt_auditoria.txt`](prompt_auditoria.txt)) a las dos IAs.

**Se mandó** ([`paquete_contexto.md`](paquete_contexto.md), 46 KB, ~12,000 tokens): 22 archivos. Son `settings.py`, `urls.py`, `requirements.txt`, los modelos, repositorios, servicios y vistas de `catalogo`, `recomendador`, `pedidos` y `asistente`, más `app_config.dart`, `api_client.dart`, `AndroidManifest.xml` y `.gitignore`.

**Se omitió:**
- La `SECRET_KEY` de `settings.py`: el script la reemplaza por `<OMITIDO: secreto>` y se detiene si llega a colarse.
- `db.sqlite3` (tiene pedidos con datos de clientes), los `.joblib`, los CSV de entrenamiento, las pantallas de Flutter y las pruebas.
- Antes de armarlo revisé `git status` (limpio) y que no hubiera `.env`, `key.properties` ni llaves `.jks`. No hay ninguno.

**Ajuste:** en la primera corrida `llama3.2` se quedó generando más de 20 minutos sin terminar. La detuve y volví a correr con un tope de 2,500 tokens de salida y `repeat_penalty`. Así terminó en 2.4 min, y qwen en 6.5 min.

---

## 3. Comparación de las dos IAs

Respuestas completas: [`respuesta_llama3_2.md`](respuesta_llama3_2.md) y [`respuesta_qwen2_5_coder_7b.md`](respuesta_qwen2_5_coder_7b.md). Revisé cada hallazgo contra el código y, cuando se podía, lo probé con el cliente de pruebas de Django.

| | `llama3.2` | `qwen2.5-coder:7b` |
|---|---|---|
| Hallazgos que dio | 10 | 10, pero solo **5 distintos** (repitió 3 veces dos de ellos) |
| ¿Siguió el formato pedido? | No: sin archivo, línea, evidencia ni severidad | Sí: severidad, archivo, código citado |
| Confirmados | 0 completos, 3 parciales | 2 |
| Falsos positivos | 6 | 3 |
| ¿Detectó lo más grave? (pedidos abiertos) | Lo rozó ("falta seguridad en pedidos") sin decir dónde ni por qué | No |

### Veredicto por hallazgo

| IA | # | Lo que dijo | Veredicto | Por qué |
|---|---|---|---|---|
| B | 1 | `DEBUG = True` en `settings.py` | ✅ **Confirmado** | Línea 10. Además, con DEBUG `ALLOWED_HOSTS` incluye `"*"`. |
| B | 2/5/7/9 | El 503 regresa `str(e)` y expone detalles técnicos | ✅ **Confirmado** (severidad baja, no alta) | El mensaje trae la ruta completa del `.joblib` en el servidor. La IA citó mal dónde: dijo `servicio.py` línea 12, pero eso está en las **vistas**. |
| B | 3 | "Validación insuficiente" en `recomendar` | ❌ **Falso positivo** | `leer_peticion` sí valida: revisa el JSON, el modelo y llama `validar_perfil()`. El error real era otro (ver H3). |
| B | 4/6/8/10 | "Leyenda de productos no activos" en `catalogo/models.py` | ❌ **Falso positivo** | `activo` nunca se le muestra al usuario. `ProductoRepository._activos()` filtra los inactivos y no llegan a la app. |
| B | 5/7/9 | `servicio.py` línea 12 tiene `except FileNotFoundError` | ❌ **Falso positivo (código inventado)** | `recomendador/servicio.py` no tiene ningún `try/except` ni `JsonResponse`. La IA "citó" código que no existe en ese archivo. |
| A | 1 | No hay autenticación | ⚠️ **Parcial** | Es cierto que la API no pide login. Pero dijo que `django.contrib.auth` "no se configuró correctamente", y está configurado normal. |
| A | 5/9 | No hay pruebas | ⚠️ **Parcial** | El backend no tenía ni un test de Django. Flutter sí tiene `flujo_test.dart`, pero no venía en el paquete. |
| A | 7 | Falta HTTPS y seguridad en pedidos | ⚠️ **Parcial** | Va en la dirección de H1 y H5, pero sin archivo ni evidencia. |
| A | 2 | `ErrorValidacion` "no se utiliza correctamente" | ❌ **Falso positivo** | `leer_peticion` la atrapa y responde 400 con el detalle. |
| A | 3 | Los errores al guardar no se le informan al usuario | ❌ **Falso positivo** | La vista convierte `SeleccionInvalida` y `ProductoSinStock` en 409 y `FileNotFoundError` en 503, con mensaje. |
| A | 4 | `RecomendadorIA` no se usa adecuadamente | ❌ **Falso positivo** | `obtener_recomendador()` regresa un `RecomendadorIA` y `servicio.recomendar` lo usa. |
| A | 8 | `AsistenteIA` no se usa correctamente | ❌ **Falso positivo** | Existe en `asistente/adaptador.py` y es el Adapter del asistente. |
| A | 6, 10 | "La base de datos" y "las URLs" no están bien configuradas | ❌ **Falso positivo / sin contenido** | No dice qué está mal. SQLite es lo que pide el proyecto, y las URLs siguen `/api/...`. |

---

## 4. Hallazgos verificados (los que quedan después de revisar)

Algunos los encontraron las IAs y otros los encontré yo al revisar sus respuestas contra el código.

| # | Severidad | Archivo | Evidencia | Riesgo | Cómo lo verifiqué | Origen |
|---|---|---|---|---|---|---|
| H1 | 🔴 Alta | `pedidos/views.py` (`pedidos`, `detalle_pedido`) | `GET /api/pedidos/` sin login lista folio y cliente de los últimos 50 pedidos; `GET /api/pedidos/<folio>/` devuelve el perfil completo | Cualquiera saca nombres y **edad, peso, estatura, IMC y si tiene lesión reciente**: datos de salud | Cliente de Django: 5 pedidos listados; el detalle trae `edad`, `peso_kg`, `imc`, `lesion_reciente`… | Yo (llama lo rozó) |
| H2 | 🔴 Alta | `tienda/settings.py:7` | `SECRET_KEY = 'django-insecure-…'` escrita en el código y subida a GitHub | Con la llave se pueden falsificar sesiones y firmas de Django | `git log` del archivo: está desde el primer commit | Yo (se omitió del paquete a propósito) |
| H3 | 🟠 Media | `recomendador/views.py` (`leer_peticion`), `asistente/views.py` | Si el cuerpo es JSON válido pero no objeto (`[]`, `5`), `cuerpo.pop(...)` o `cuerpo.get(...)` truena | **HTTP 500** en `/recomendar/`, `/pedidos/` y `/asistente/` | `POST` con `[]` → 500 en los tres | Yo (qwen apuntó a la vista correcta con un diagnóstico equivocado) |
| H4 | 🟠 Media | `tienda/settings.py:10-12` | `DEBUG = True` y `"*"` en `ALLOWED_HOSTS` | Si se despliega así, los errores muestran trazas y configuración | Lectura del archivo | qwen |
| H5 | 🟠 Media | `android/app/src/main/AndroidManifest.xml` | `android:usesCleartextTraffic="true"` en el manifest **principal**, no solo en debug | El APK de release manda pedidos y perfiles por HTTP sin cifrar | Lectura del archivo | Yo |
| H6 | 🟡 Baja | `recomendador/views.py`, `pedidos/views.py`, `asistente/views.py` | `JsonResponse({"error": str(e)}, status=503)` | El cliente ve la ruta completa del servidor | Prueba con un `FileNotFoundError` simulado | qwen |
| H7 | 🟡 Baja | `pedidos/views.py` | `POST /api/pedidos/` no tiene llave de idempotencia | Un doble toque en "Confirmar" crea 2 pedidos y descuenta stock 2 veces | Lectura del código | Yo |
| H8 | 🟡 Baja | repo | `backend/db.sqlite3` está en git | Se suben pedidos de prueba con perfiles | `git ls-files` | Yo |

---

## 5. Cambios hechos después de la auditoría

En el repo de **KitAte**:

| Hallazgo | Cambio | Archivo |
|---|---|---|
| H2, H4 | `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` se leen de variables de entorno (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`). Con `DJANGO_DEBUG=0` y sin llave, el servidor **no arranca**. Sin variables sigue en modo desarrollo, para no romper la demo. | `backend/tienda/settings.py` |
| H3 | Si el cuerpo no es un objeto JSON (o no es UTF-8), responde **400** en vez de 500. | `backend/recomendador/views.py`, `backend/asistente/views.py` |
| H6 | El 503 dice "el modelo no está disponible, intenta más tarde" y la ruta se va al log. | `recomendador/views.py` (`modelo_no_disponible`), usada también en `pedidos` y `asistente` |
| Pruebas | Primer `tests.py` del backend: 5 pruebas, todas en verde (4 de cuerpo inválido → 400 y 1 de que el 503 no filtra la ruta). | `backend/recomendador/tests.py` |

```
$ python manage.py test
Ran 5 tests in 0.025s
OK
```

Después de los cambios, `/api/opciones/`, `/api/asistente/` y `GET /api/pedidos/` siguen respondiendo 200.

---

## 6. Pendientes y por qué

| Hallazgo | Por qué no se arregló todavía | Qué haría |
|---|---|---|
| H1 (pedidos abiertos) | La pantalla de Flutter "Mis pedidos" usa `GET /api/pedidos/` para mostrar los recientes, y la app no tiene cuentas de usuario. Cerrarlo hoy rompe esa pantalla antes de la demo. | Guardar en el celular (SharedPreferences) los folios que creó ese dispositivo y pedir solo esos, quitar `GET /api/pedidos/` y, a futuro, agregar login. |
| H2 (llave en el historial) | Quitarla del código no la borra del historial de git. | **Generar una llave nueva** para cualquier despliegue (`DJANGO_SECRET_KEY`). La vieja se da por quemada. |
| H5 (HTTP en claro) | La demo usa el backend por HTTP en la red local (`10.0.2.2` o la IP de la PC). | Mover `usesCleartextTraffic` a `src/debug/AndroidManifest.xml` cuando el backend tenga HTTPS. |
| H7 (doble toque) | Requiere cambiar app y backend a la vez. | La app genera una llave por intento y el backend la guarda única junto al pedido. |
| H8 (`db.sqlite3` en git) | Es un comando de git, no de código. | `git rm --cached backend/db.sqlite3` y agregarlo a `.gitignore`. |

---

## 7. Conclusión

- **Ninguna de las dos IAs encontró el problema más grave** (H1). Lo encontré al revisar a mano por qué `llama3.2` decía "falta seguridad en pedidos".
- **`qwen2.5-coder` fue más útil** porque citó archivos y código, pero también inventó código que no existe y repitió hallazgos para completar los 10 que le pedí. Si no hubiera abierto `servicio.py`, habría "corregido" algo que no está ahí.
- **`llama3.2` sirvió casi nada como auditor**: 10 frases generales sin evidencia. Lo único rescatable fue señalar que el backend no tenía pruebas.
- Con modelos chicos y locales, la IA sirve como **lista de lugares dónde mirar**, no como veredicto. El valor estuvo en verificar cada punto con el código y con pruebas reales.
