# Camino de POST /pedidos, notas mías

Voy a anotar por dónde pasa una petición POST /pedidos, con los nombres que usa Django, y marco qué pasos ya me los da el framework hecho, no son un patrón GoF que yo tenga que escribir.

1. El navegador manda el POST a /pedidos, viene del form de pedidos/nuevo.html, con csrf_token.

2. El WSGI handler de Django recibe la petición. Esto es el Front Controller, un único punto de entrada que recibe todas las peticiones y las despacha. No lo escribo yo, ya viene armado por Django (WSGIHandler en config/wsgi.py).

3. MIDDLEWARE. Antes de llegar a mi vista, la petición pasa por la lista de MIDDLEWARE en settings.py (Security, SessionMiddleware, Common, CsrfViewMiddleware, Auth, Messages, Clickjacking). Esto es la cadena de responsabilidades (Chain of Responsibility), cada middleware puede procesar la request y pasarla al siguiente, o cortar la cadena, por ejemplo el CSRF middleware corta con 403 si no viene el token. Tampoco lo escribo yo, Django ya instancia la cadena a partir de esa lista.

4. config/urls.py. El ROOT_URLCONF mira urlpatterns y ve el include de entregas.urls, así que delega en las urls de mi app.

5. entregas/urls.py. Aquí sí decidí yo el mapeo, path pedidos apuntando a views.crear_pedido. Esto asocia la URL con la función de vista.

6. La vista crear_pedido en entregas/views.py. Es un Page Controller delgado, solo lee request.POST, llama a registrar_pedido() y devuelve el redirect. No mete SQL, no mete sesión, no decide medios de entrega ni cobros.

7. entregas/servicios.py con registrar_pedido(origen, destino, peso_kg). Aquí vive la lógica de negocio, en ese momento mínima, crea el Pedido. Es la capa de servicio, separada de la vista a propósito.

8. El modelo Pedido en entregas/models.py. Pedido.objects.create() guarda en la base vía el ORM. El id que genera Django es el folio, no hice un campo aparte.

9. HttpResponseSeeOther, el redirect 303. La vista regresa un redirect explícito con Location a /pedidos/<id> y status 303. Esto es el patrón Post-Redirect-Get, si el usuario recarga después, el navegador repite el GET, no el POST, así que nunca se duplica el pedido.

10. El navegador hace el GET a /pedidos/<id>.

11. Otra vez pasa por el Front Controller y el MIDDLEWARE, los pasos 2 y 3, pero ahora como GET.

12. La vista seguimiento_pedido. Busca el pedido por id, arma un diccionario ya listo con folio, estado y un eta fijo en 30 min, y se lo pasa al render.

13. La plantilla seguimiento.html hace extends de entregas/base.html y solo rellena folio, estado y eta. No hace consultas ni .all(), solo pinta lo que ya le mandó la vista.

## Resumen de qué no es mi patrón

Front Controller, paso 2, ya lo trae Django, es el WSGI handler.

Chain of Responsibility, paso 3, ya lo trae Django, es el MIDDLEWARE.

## Lo que sí escribí yo

Page Controller, la vista delgada.

Post-Redirect-Get, el 303 con Location al seguimiento.

La separación vista, servicio (registrar_pedido) y modelo, para no mezclar SQL con la vista.
