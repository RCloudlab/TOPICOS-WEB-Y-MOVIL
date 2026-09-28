# Ensayo de tres minutos, si mañana hay triciclo

Voy a contestar la pregunta mirando el código real, no de memoria, y luego lo comprobé de verdad.

Mi apuesta antes de tocar nada. Abro entregas/dominio/medios.py para agregar la clase EntregaTriciclo, y entregas/dominio/fabrica.py para agregar una línea al diccionario MEDIOS. Más una prueba nueva en entregas/tests.py. La vista, el adaptador de IA, la plantilla y registrar_pedido no deberían necesitar tocarse, porque registrar_pedido solo llama a crear(sugerencia.medio) y medio.planear(), nunca conoce los nombres de las clases concretas.

Lo hice de verdad. Agregué EntregaTriciclo en medios.py con su propia regla (aplica si el paquete pesa 8 kg o menos y la distancia es de 6 km o menos), y agregué la entrada triciclo en el diccionario de fabrica.py. Corrí los tests después de cada archivo y solo edité esos dos más tests.py, le agregué dos pruebas de plan y un caso en la fábrica. No abrí la vista, no abrí ia.py, no abrí registrar_pedido, no abrí ninguna plantilla. python manage.py test pasó de 29 a 31 pruebas, todas en verde. La apuesta se cumplió, no hubo que reportar ningún defecto del Día 3. Decidí dejar el triciclo en el código porque ya quedó probado y es un medio válido más, no hace daño dejarlo.

Segundo caso, si el proveedor de IA cambia route_hint por vehicle. Miré AdaptadorProveedorIAJson.sugerir en entregas/dominio/ia.py, la única línea que lee esa clave es la que hace crudo["route_hint"]. Cambiar el nombre de la clave es una edición de una línea dentro de ese mismo adaptador (y si quisiera simular la respuesta nueva, también dentro de ProveedorIAJson, que está en el mismo archivo). registrar_pedido, la vista y los medios no saben que existe route_hint, así que no cambian nada.

## Las tres preguntas del cierre

Qué problema resolví. Que cada medio de entrega tenga su propia regla sin llenar el servicio de ifs (Strategy), que lo que dice un proveedor de IA ajeno no se riegue por todo el código (Adapter), que convertir un string en la clase correcta no obligue a repetir un switch en cada lugar (fábrica simple), que guardar el pedido y cobrar sea una sola operación con aviso después y sin duplicar por doble clic (transacción e idempotencia), que la IA caída no tumbe el flujo (timeout y respaldo), y que el panel HTML y una futura app puedan ver el mismo pedido sin duplicar la consulta (JSON reutilizando consultar_seguimiento).

Por qué esta solución es adecuada. Porque cada patrón resuelve exactamente el problema que tenía enfrente y nada más. No hay una jerarquía de fábricas por encima de la fábrica simple, no hay un bus de eventos por encima de on_commit, no hay un framework de API por encima de JsonResponse. El tamaño de la solución es el tamaño del problema.

Qué complejidad introduje. Dos capas nuevas de indirección, el dominio (entregas/dominio) que no conoce Django, y la separación entre consultar (consultar_seguimiento, consultar_inicio) y registrar (registrar_pedido). Es complejidad real, pero es la mínima necesaria para que un medio nuevo, un proveedor de IA nuevo, o un consumidor nuevo como la app no obliguen a tocar código que no tiene que ver con ellos.
