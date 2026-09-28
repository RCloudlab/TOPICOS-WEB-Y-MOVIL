# Empresa de Entregas (Día 5)

Notas mías para defender el repo sin tener al profe al lado.

## a) Cómo se corre

```
python -m venv .venv
.venv\Scripts\activate
pip install Django
python manage.py migrate
python manage.py runserver
```

Rutas principales

GET /pedidos/nuevo, formulario para crear un pedido (panel HTML)
POST /pedidos, da de alta el pedido y redirige (303) al seguimiento
GET /pedidos/<id>, seguimiento en HTML, con mapa y ETA
GET /api/pedidos/<id>, el mismo folio en JSON con folio, estado y eta
GET /api/inicio, lista de pedidos (folio, estado, eta) en una sola respuesta, para la pantalla de inicio de la app
GET /reporte, tabla HTML con todos los pedidos

Para correr las pruebas

```
python manage.py test
```

31 pruebas, todas en verde.

## b) Qué ya traía Django y no reescribí

El handler WSGI y urls.py son el Front Controller, un solo punto de entrada que despacha todo, no lo armé yo.

MIDDLEWARE en settings.py es la cadena de responsabilidades (Chain of Responsibility) que ya trae Django, sesión, CSRF, clickjacking, etc, cada uno decide seguir o cortar.

Las plantillas (extends, render) hacen de Template View, reciben un diccionario ya armado y solo rellenan huecos, no las escribí desde cero, son el sistema de templates de Django.

transaction.atomic() es mi Unit of Work, agrupa guardar el pedido y el cobro como una sola operación que se confirma o se deshace junta.

transaction.on_commit() es el mecanismo que ya trae Django para avisar después de que el COMMIT ya pasó, no antes.

redirect y mi HttpResponseRedirectBase con 303 es el Post-Redirect-Get que ya soporta Django, no inventé un patrón de redirección.

El ORM de Django es Active Record (cada modelo sabe guardarse y consultarse a sí mismo). No lo disfracé de Repository ni le puse una capa encima que no hacía falta.

## c) Mapa de archivos (patrones)

Adapter, entregas/dominio/ia.py. Los adaptadores (AdaptadorProveedorIAJson, AdaptadorProveedorIAXml) traducen el formato ajeno de cada proveedor de IA (JSON con route_hint y score, XML con vehicle) al único idioma del dominio (Sugerencia). Resuelve que un formato externo no se riegue por el resto del código.

Strategy, entregas/dominio/medios.py. Cada medio (EntregaCamioneta, EntregaMotocicleta, EntregaBicicleta, EntregaDron, EntregaTriciclo) tiene su propia regla de planear(). Resuelve que registrar_pedido no tenga un if o switch por medio.

Fábrica simple, entregas/dominio/fabrica.py. Un diccionario string a clase (crear(tipo)). Resuelve convertir el nombre de la sugerencia en el objeto correcto sin repetir el mapeo en cada lugar que lo necesite.

El trámite, registrar_pedido en entregas/servicios.py. Orquesta todo, pide la sugerencia a la IA (con timeout y reintento), crea el medio con la fábrica, planea, guarda pedido y cobro en una transacción, agenda el aviso post commit, y respeta la clave de idempotencia para no duplicar en un doble clic. Resuelve el flujo completo de negocio sin que la vista sepa nada de sus detalles.

## d) Qué rechacé y por qué

El punto 7 del enunciado (Event Sourcing, CQRS, Redux global para generar un PDF de guía). El trámite real ahí es autenticar, consultar un pedido y generar un archivo. Ese tamaño de infraestructura es para reconstruir historial completo o separar lecturas y escrituras a gran escala, no para un botón de descargar guía.

Abstract Factory. No hay familias de objetos relacionados que crear juntas, solo un tipo de objeto (MedioDeEntrega) a partir de un string. Una fábrica simple ya alcanza.

Factory Method. No hay subclases que redefinan un gancho de creación, no hay esa jerarquía.

Singleton. Nada en este repo necesita una única instancia global controlada. Los objetos que se reutilizan (RECOMENDADOR_POR_DEFECTO) son módulo level normales de Python, no necesitan el patrón.

API Gateway o un BFF aparte. /api/inicio y /api/pedidos/<id> son dos rutas más dentro del mismo proyecto Django. No hay múltiples servicios detrás que orquestar.

Django REST Framework. JsonResponse alcanza para dos endpoints de solo lectura, no hace falta un framework de serialización completo.

Circuit breaker complicado. El inconveniente de la IA caída se resuelve con un timeout y un reintento con tope, no hace falta contar fallas ni abrir y cerrar un circuito.

## Verificación

La vista y la plantilla no contienen EntregaDron, route_hint ni SQL. Cumple. Revisé entregas/views.py y entregas/templates con búsqueda de esas palabras, cero resultados.

route_hint, score y vehicle aparecen solo dentro de los adaptadores. Cumple. Las únicas apariciones en todo el proyecto están en entregas/dominio/ia.py.

No hay código muerto ni archivos v2. Cumple. Sin archivos v2, old o backup, sin imports sin usar en las vistas ni el dominio.

No se agregó ninguna dependencia fuera de Django. Cumple. pip list dentro del venv solo muestra Django y sus propias dependencias (asgiref, sqlparse, tzdata). No usé biblioteca de PDF porque rechacé ese punto del enunciado.
