# Notas del día 4

## Uno, qué resolví con cada cambio

El inconveniente 3 era que la vista de seguimiento y el reporte iban a terminar metiendo QuerySets en la plantilla o repitiendo la misma consulta en dos lados. Lo resolví con consultar_seguimiento(folio), hace la consulta una vez, arma un diccionario ya listo (folio, estado, medio, motivo, eta, lat y lng) y tanto la vista de seguimiento como /reporte llaman a esa misma función, nunca repiten la consulta. La plantilla solo pinta lo que le llega, ni .all ni relaciones. Esto no es ningún patrón raro, es nomás no ensuciar la plantilla con lógica de datos.

El inconveniente 4 era el dinero, si guardo el pedido y el cobro por separado y algo truena a medias, puedo terminar con un pedido sin cobro o un cobro sin pedido. Por eso ambos van dentro de transaction.atomic(), si el cobro falla, se deshace también el pedido, no queda nada a medias. El aviso (el print o log de pedido registrado) lo separé con transaction.on_commit, que ya trae Django, así solo se dispara si la transacción de verdad se guardó, y si el aviso mismo truena, lo atrapo con logging para que no tumbe la respuesta al usuario. No usé post_save porque esas señales se disparan dentro de la transacción, antes del commit, entonces si el aviso fallara ahí adentro se podría revertir el pedido por un error que no tiene nada que ver con guardar datos.

La idempotencia, o sea el doble clic, la resolví con una clave de intento que el formulario manda oculta, generada con UUID cada vez que se pinta /pedidos/nuevo. registrar_pedido primero busca si ya hay un cobro con esa clave, si lo hay, regresa el pedido de ese cobro en vez de crear otro. La restricción unique en clave_idempotencia es la que ya trae Django y es la que de verdad protege contra una carrera si llegaran dos peticiones casi al mismo tiempo.

Lo del inconveniente 6, la IA que se cae, lo resolví envolviendo la llamada al recomendador en un timeout configurable (IA_TIMEOUT_SEGUNDOS) y solo reintento una vez si el error es temporal (timeout o falla transitoria del proveedor). Si es un error de validación, la IA respondió basura, no reintento, no tiene caso. Si después del reintento sigue sin responder, o si IA_ACTIVA está en False, uso la camioneta de respaldo con el motivo fijo IA no disponible. El cobro nunca se reintenta porque reintentar un cobro sí puede cobrar dos veces, ahí no hay ambigüedad que valga la pena arriesgar.

De Django usé tal cual el sistema de plantillas, para no meter consultas ahí, transaction.atomic, transaction.on_commit, HttpResponseRedirectBase para el 303, y unique=True en el modelo para la restricción de idempotencia. Nada de eso lo escribí yo desde cero.

## Dos, doble clic y por qué Observer no basta

Si el cliente pulsa crear dos veces, el PRG, el redirect 303 después del POST, ya evita que una recarga de la página reenvíe el POST, porque el navegador solo repite el GET. Pero el doble clic real, dos POST distintos uno tras otro antes de que llegue el redirect, no lo arregla el PRG, lo arregla la clave de idempotencia en el servidor, aunque lleguen dos POST, la segunda llamada a registrar_pedido encuentra el cobro ya hecho y regresa el mismo pedido. Si hay dinero de por medio hacen falta las dos cosas, el PRG evita la recarga tonta, la clave evita el doble cobro real.

Observer, o las señales de Django, no sustituye la transacción porque el aviso ocurre después del commit, cuando el pedido y el cobro ya están guardados o ya se revirtieron los dos juntos. Un Observer no garantiza que dos operaciones relacionadas, guardar pedido y guardar cobro, se confirmen como una sola unidad, eso es exactamente lo que hace atomic, no un patrón de notificación.

## Tres, qué no metí y por qué

No metí Event Sourcing ni CQRS porque aquí no hay que reconstruir historial ni separar lecturas de escrituras a ese nivel, el problema era mucho más chico, una consulta limpia, una transacción y un timeout. No metí un bus de eventos casero porque transaction.on_commit ya resuelve avisar después de guardar sin inventar infraestructura nueva. Y no metí un circuit breaker con contador de fallas y estados, porque lo que pedía el enunciado era nomás un timeout con un reintento y un respaldo fijo, un circuit breaker de verdad es para cuando quieres dejar de intentarle a un servicio caído por un rato, y aquí ese nivel de complejidad no resuelve nada que el timeout más respaldo no resuelva ya.
