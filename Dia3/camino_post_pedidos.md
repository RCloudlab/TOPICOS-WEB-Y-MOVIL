# Camino de POST /pedidos (notas mías)

Voy a anotar por dónde pasa una petición POST /pedidos, con los nombres que usa Django, y marco qué pasos ya me los da el framework hecho (no son un patrón GoF que yo tenga que escribir).

1. **El navegador manda el POST** a `/pedidos` (viene del form de `pedidos/nuevo.html`, con `{% csrf_token %}`).

2. **El WSGI handler de Django recibe la petición.** Esto es el **Front Controller**: un único punto de entrada que recibe TODAS las peticiones y las despacha. No lo escribo yo, ya viene armado por Django (`WSGIHandler` en `config/wsgi.py`).

3. **MIDDLEWARE.** Antes de llegar a mi vista, la petición pasa por la lista de `MIDDLEWARE` en `settings.py` (Security, SessionMiddleware, Common, CsrfViewMiddleware, Auth, Messages, Clickjacking). Esto es la **Cadena de Responsabilidades (Chain of Responsibility)**: cada middleware puede procesar la request y pasarla al siguiente, o cortar la cadena (por ejemplo el CSRF middleware corta con 403 si no viene el token). Tampoco lo escribo yo — Django ya instancia la cadena a partir de esa lista.

4. **config/urls.py.** El `ROOT_URLCONF` mira `urlpatterns` y ve `path('', include('entregas.urls'))`, así que delega en las urls de mi app.

5. **entregas/urls.py.** Aquí sí decidí yo el mapeo: `path("pedidos", views.crear_pedido, ...)`. Esto asocia la URL con la función de vista.

6. **La vista `crear_pedido` (entregas/views.py).** Es un **Page Controller** delgado: solo lee `request.POST.get(...)`, llama a `registrar_pedido(...)` y devuelve el redirect. No mete SQL, no mete sesión, no decide medios de entrega ni cobros.

7. **entregas/servicios.py → `registrar_pedido(origen, destino, peso_kg)`.** Aquí vive la lógica de negocio (mínima por ahora): crea el `Pedido`. Es la capa de servicio, separada de la vista a propósito.

8. **El modelo `Pedido` (entregas/models.py).** `Pedido.objects.create(...)` guarda en la base vía el ORM. El `id` que genera Django es el folio, no hice un campo aparte.

9. **`HttpResponseSeeOther` (redirect 303).** La vista regresa un redirect explícito con `Location: /pedidos/<id>` y status 303. Esto es el patrón **Post-Redirect-Get**: si el usuario recarga después, el navegador repite el GET, no el POST, así que nunca se duplica el pedido.

10. **El navegador hace el GET** a `/pedidos/<id>`.

11. **Otra vez pasa por el Front Controller y el MIDDLEWARE** (pasos 2 y 3), pero ahora como GET.

12. **La vista `seguimiento_pedido`.** Busca el pedido por id, arma un diccionario ya listo (`folio`, `estado`, `eta` fijo en "30 min") y se lo pasa al `render`.

13. **La plantilla `seguimiento.html`** hace `{% extends "entregas/base.html" %}` y solo rellena `{{ folio }}`, `{{ estado }}`, `{{ eta }}`. No hace consultas ni `.all()`, solo pinta lo que ya le mandó la vista.

## Resumen de qué NO es "mi" patrón

- **Front Controller** (paso 2): ya lo trae Django, es el WSGI handler.
- **Chain of Responsibility** (paso 3): ya lo trae Django, es el `MIDDLEWARE`.

## Lo que sí escribí yo

- **Page Controller** (la vista delgada).
- **Post-Redirect-Get** (el 303 con Location al seguimiento).
- La separación vista → servicio (`registrar_pedido`) → modelo, para no mezclar SQL con la vista.
