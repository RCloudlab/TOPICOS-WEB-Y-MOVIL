# Misiones: patrones de software para aplicaciones web

## El problema

Una universidad pública mantiene el alta de materias, el pago de inscripción, las constancias y las becas en decenas de páginas sueltas (PHP, ASP clásico y un par de servicios nuevos). Se requiere un portal web único para el siguiente ciclo.

Estado actual documentado por control escolar y caja:

- Cada trámite es un archivo distinto. En todos se copia el mismo bloque de «¿hay sesión?», el mismo registro en bitácora y el mismo encabezado HTML. Cambiar la regla de caducidad de sesión obliga a tocar cuarenta archivos; siempre se olvida uno.
- El pago de inscripción admite tarjeta, transferencia SPEI y referencia de ventanilla. El script `pagar.php` es un switch de doscientas líneas. Cada banco nuevo obliga a editarlo. El protocolo del banco habla de «créditos» y códigos 00/01; el reglamento interno habla de «pago de inscripción» y estados pendiente / acreditado / rechazado.
- La plantilla del kardex ejecuta consultas SQL para armar la tabla de calificaciones. Los reportes de constancias duplican esas consultas con otro formato.
- Cuando el pago se acredita, el mismo script llama a control escolar (alta de materias), dispara un correo al estudiante y avisa a caja. Si el correo falla, a veces no se registra el alta. Si el estudiante pulsa dos veces «pagar» porque la página tarda, se han cobrado dos cargos.
- La app móvil y el kiosco de biblioteca deben mostrar el mismo trámite. La app pide un JSON mínimo (folio, saldo, plazo); el kiosco pide una página HTML con el escudo y la tabla de vencimientos. Hoy el equipo de la app hace doce peticiones para pintar la pantalla de inicio.
- El servicio de un banco y el de un validador de CURP externo se caen con frecuencia. Mientras no responden, el estudiante ve la rueda de espera y no puede ni consultar el kardex, que no depende de esos colaboradores.
- Un proveedor propone, para la descarga de una constancia en PDF, Event Sourcing, CQRS, una malla de microservicios y un almacén global Redux en el navegador. El trámite de la constancia es: autenticar, consultar un registro ya existente y generar un archivo.
- El portal puede construirse en Spring, Laravel o Express: el análisis no espera un marco concreto, pero sí espera usar lo que el marco ya instancia (enrutador, middleware, transacción del ORM) sin copiar un diagrama UML al lado.

## Qué se evalúa

| Criterio | Se espera |
|---|---|
| Composición | El portal no se etiqueta con un solo patrón. Cada conflicto tiene una estructura y una capa. |
| Cuándo y por qué | Se justifica con una fuerza del problema, no con «porque sale en el temario». |
| Vecino rechazado | Adapter no se confunde con Facade; Observer no sustituye a Unit of Work. |
| Marco | Se nombra qué no hay que reescribir si el equipo usa Spring, Laravel o Express. |
| Sobreingeniería | Se rechaza el catálogo donde no hay problema. |

---

## Misión 1 — El portal no es un patrón

| # | Problema | Capa | Patrón(es) | Por qué ese y no el vecino | Cuándo NO aplicaría |
|---|----------|------|-----------|------------------------------|----------------------|
| 1 | Cada trámite repite el chequeo de sesión, la bitácora y el encabezado HTML | Políticas transversales | **Chain of Responsibility** (middleware/pipeline del framework, tipo Front Controller) | No es Decorator: Decorator envuelve *un* objeto para añadirle comportamiento; aquí se necesita una tubería que *toda petición* atraviesa antes de llegar al trámite. El framework (Spring interceptors, Express middleware, Laravel middleware) ya la instancia — no hay que reescribirla | Si solo existiera un trámite, meter una pipeline es sobreingeniería; bastaría una función compartida |
| 2 | `pagar.php` es un switch de 200 líneas; cada banco nuevo obliga a tocarlo; el protocolo del banco habla en "créditos"/códigos 00-01 y el reglamento en "pendiente/acreditado/rechazado" | Aplicación/dominio + Integración | **Strategy** (un objeto por medio de pago) + **Adapter** (traduce vocabulario del banco al del dominio) | No es Facade: Facade simplifica el *acceso* a un subsistema sin traducir su vocabulario; aquí hay una traducción semántica real (00/01 → acreditado/rechazado), eso es Adapter | Si solo hubiera un banco fijo y sin planes de cambiar, el switch simple es más barato que el andamiaje de Strategy |
| 3 | El kardex ejecuta SQL directo; las constancias duplican esas consultas; un proveedor propone Event Sourcing + CQRS + microservicios + Redux para *descargar un PDF* | Datos | **Repository** (una sola consulta reutilizada por kardex y constancias) | No es Active Record: el registro se lee desde dos vistas distintas (tabla vs. PDF), conviene separar acceso a datos de la representación, que es justo el rol de Repository, no mezclar persistencia y objeto de dominio | Aquí mismo: para la constancia el trámite real es *autenticar → Repository.consultar() → generar archivo*. Event Sourcing/CQRS/microservicios/Redux es catálogo sin problema — se rechaza explícitamente |
| 4 | Al acreditarse el pago, el mismo script llama a control escolar, envía correo y avisa a caja; si el correo falla a veces no se registra el alta; doble clic produce doble cobro | Aplicación/dominio | **Observer / Domain Event** (desacopla las tres reacciones) **+ Unit of Work + Idempotent Receiver** (para el doble cobro) | Observer resuelve el desacoplamiento de notificaciones, pero *no* resuelve la atomicidad ni el doble clic — eso exige una frontera transaccional (Unit of Work) y una clave de idempotencia. Confundir "ya desacoplé con Observer" con "ya resolví la consistencia" es el error típico | Si solo hubiera un efecto colateral y el orden no importara, un simple callback basta, sin necesidad de un bus de eventos formal |
| 5 | La app pide JSON mínimo, el kiosco pide HTML con escudo; hoy la app hace 12 peticiones para pintar la pantalla | Presentación | **Facade** (agrega las 12 llamadas en una) + **Builder/renderer** distinto por cliente | No es Adapter: Adapter traduce la interfaz de *un* objeto; aquí se agregan *varios* subsistemas en una sola llamada simplificada para el cliente — eso es Facade | Si solo hubiera un cliente, no hace falta capa de agregación; se expone el dominio directo |
| 6 | El servicio del banco y el validador de CURP se caen seguido; mientras tanto ni el kardex (que no depende de ellos) responde | Integración | **Circuit Breaker + Bulkhead** | No es solo Retry: reintentar no evita que las peticiones colgadas agoten el pool de conexiones/hilos y arrastren al kardex; Bulkhead aísla los recursos, Circuit Breaker deja de llamar al servicio caído | Si el kardex realmente dependiera de esos servicios, aislarlos no resolvería nada — el patrón solo tiene sentido cuando hay independencia real que hoy se está desperdiciando |

---

## Misión 2 — La petición de pago, paso a paso

| Paso | Objeto/mecanismo | Patrón que realiza |
|------|-------------------|---------------------|
| 1 | `POST /inscripciones/{id}/pago` llega al enrutador del framework | **Front Controller** (dado por Spring/Laravel/Express — no se reescribe) |
| 2 | Middleware de autenticación verifica sesión | **Chain of Responsibility** (un eslabón de la pipeline) |
| 3 | Middleware de bitácora registra la petición | **Chain of Responsibility** (otro eslabón, mismo mecanismo, no una capa nueva) |
| 4 | Controlador delega a `PagoService.pagarInscripcion(...)` | Delegación simple del Front Controller hacia el servicio de aplicación |
| 5 | `PagoService` elige el objeto de medio de pago (tarjeta/SPEI/ventanilla) | **Strategy** |
| 6 | `BancoAdapter` traduce la petición al protocolo del banco y su respuesta (00/01) de vuelta a `pendiente/acreditado/rechazado` | **Adapter** |
| 7 | Antes de escribir, se valida una clave de idempotencia (folio + intento) para que un doble clic no duplique el cargo | **Idempotent Receiver** |
| 8 | El repositorio persiste el estado del pago dentro de la transacción que ya da el ORM del framework | **Repository + Unit of Work** (transacción del ORM, no una capa nueva) |
| 9 | Al confirmar el commit, se publica el evento `PagoAcreditado` | **Observer / Domain Event** |
| 10 | Suscriptores independientes reaccionan: alta de materias, correo, aviso a caja (idealmente vía cola, así un correo caído no bloquea el alta) | **Observer** (uno por cada efecto colateral) |
| 11 | Se responde al cliente con folio y estado, sin esperar a los observers asíncronos | Cierre de la petición — ninguna capa extra |

No se inventa una "capa de servicio de dominio" separada del controlador ni un "orquestador" aparte del evento: el enrutador, el middleware y la transacción del ORM del framework ya cubren esos roles.
