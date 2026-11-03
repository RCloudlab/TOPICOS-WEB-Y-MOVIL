           ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
             EXAMEN — MICROSERVICIOS, GATEWAY Y EL MONOLITO
                                CON API
              Tópicos Selectos de Tecnologías Web y Móvil

                            Eduardo Alcaraz
           ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


Nombre:____Rodrigo Vega Espinoza______________ Calificación :_________


Indicaciones
════════════

  Este examen *no* se aprueba de memoria. Casi todas las preguntas
  tienen una respuesta que «suena bien» y está mal, o dos opciones
  defendibles donde se califica el argumento.

  Reglas:

  • Expliquen el *porqué*. Una conclusión sin razonamiento vale la mitad
    (o menos).
  • Cuando digan «depende», digan *de qué*.
  • No hace falta código que compile; sí hace falta que el diseño cierre
    (quién llama a quién, qué pasa si algo falla, qué ve el cliente).
  • Pueden dibujar. Un dibujo contradictorio con el texto resta.

  Puntaje: *100 puntos* (10 × 10).


1 — La frase del compañero (10 puntos)
══════════════════════════════════════

  En el pizarrón quedó:

        La API separa clientes del servidor; los microservicios
        separan servidores entre sí.

  Un compañero dice: «Entonces, si mi monolito Django expone una API y
  además lo meto en Docker, ya cumplí las dos mitades de la frase.»

  a) Desarmen su argumento. ¿Qué parte de la frase cree cumplir con la
  API? ¿Qué parte cree cumplir con Docker? ¿En qué se equivoca en cada
  una? 
Con la API cumple una pero parte pero con su justificación de Docker ahí esta mal, por que Docker solo empaqueta el proeso, un contenedor con todo Django sigue siendo un solo proceso, un depleoy una base de datos y un solo punto de falla

  b) Den un contraejemplo mínimo: mismo código Django, *con* API y *con*
  Docker, que *sigamos* pudiendo llamar monolito. ¿Qué tendría que
  añadir (o partir) para que deje de serlo?
Proyecto Django con las apps, usuarios, pedidos y recomendar expuestas con DRF con un solo dockerfile, un solo contenedror y una sola BD tiene API y Docker y sigue siendo monolito. Pero deja de serlo cuando partes el código en procesos que se despliegan por separado. Cada uno necesita su propia imagen, su propio ciclo de versión y sus propios datos, y se hablan por la red de un contrato

  c) ¿La frase del pizarrón habla de *tecnologías* (Docker, REST) o de
  *límites de proceso / despliegue*? Defiendan su lectura con lo que
  vieron en clase.
La frase habla de limites de proceso y despliegue no de Tenologias. en clase vimos microservicios que son un estilo de arquitectura, la prueba es que si puedo apagar o desplegar recomendar sin tocar pedidos, Si no puedo, no hay separacion+


2 — Tres rutas, una trampa (10 puntos)
══════════════════════════════════════

  El equipo muestra este `urls.py' de un solo proyecto Django:

  ┌────
  │ path("usuarios/", ...),
  │ path("pedidos/", ...),
  │ path("recomendar/", ...),
  └────

  y este `docker-compose.yml':

  ┌────
  │ services:
  │   api:
  │     build: .
  │     ports: ["8000:8000"]
  │     deploy:
  │       replicas: 3
  └────

  Afirman: «Tres rutas + tres réplicas = microservicios con alta
  disponibilidad.»

  a) Separen las dos ideas que mezclaron (rutas vs réplicas). ¿Qué
  problema resuelve cada una y cuál *no* resuelve?
De primero las rutas organizan el codigo dentro de un mismo proceso. Dan orden, pero no independencia, si recomendar cae se caen las otras 3, las replicas son copias del minimo monolito, dan disponibilidad y escalan pero nunca se separan las responsabilidades, ademas tres replicas con el puerto fijo, van a chcoar sin un balanceador

  b) Si una de las tres réplicas se cae a mitad de un `POST /pedidos',
  ¿el sistema dejó de ser monolito? ¿Por qué sí o por qué no?
No deja de ser monolito por que el que lo define es la unidad de despliegue, no si está sano. Y lo que pasas es que ese POST se pierde y el vcliente ve un error, si reintenta sin un id de pedidod, puede duplicar el pedido

  c) Rediseñen *solo con palabras* el `compose' para que sí ilustre
  microservicios (nombres de servicios y responsabilidades; no hace
  falta YAML perfecto). ¿Cuántas *imágenes distintas* mínimo y por qué
  esa cantidad?
Gateway: Entrada, autenticacion y ruteo
Usuarios: Su propia BD
Pedidos: Su propia BD y llamando a recomendar
Recomendar cargando el .joblib
Minimo son 3 imagenes propias, usuarios, pedidos y recomendar, por que cada uno tiene su codigo y se despliega aparte, y el gateway usa la imagen oficial de nginx asi que en total serian 4. Si son menos dos responsabilidades vuelven a compartir el mismo despliegue

3 — El gateway que «hace de más» (10 puntos)
════════════════════════════════════════════

  Les proponen este diseño «para no complicar»:

        Un solo contenedor nginx+Python que: valida el JWT, elige
        el medio con el `.joblib', guarda el pedido en SQLite,
        manda el correo y devuelve el HTML.

  Lo llaman «API Gateway».

  a) ¿Es un gateway? Si no, ¿qué es? Usen la analogía del recepcionista
  (o otra) y digan qué oficios mezclaron.
Este no es gateway (Aprendí a la mala) es un monolito con ngix al frente, es como un recepcionastia, el gateway decde quien pasa y a donde pero sin ser director, el recepcionista tambien calcula envio y guarda en la basa y manda correos, es decir mezclaron lo que hace el protero, logistica basededatos y mensajeria 

  b) Mencionen *tres* consecuencias malas de ese diseño cuando el modelo
  pesado se reentrena cada semana y el correo empieza a fallar.
1.- Cada reentrenamiento semanal obliga a redeplegar todo, y se cae hasta el login
2.- Si el correo falla el pedido aparecera como fallido y si lo vuelve a poner se duplica
3.- EL modelo pesado consume RA y CPU que necesita validar el JWT y SQLite dentro del contenedor no permitira relicar y se perdera si se vuelve a recrear

  c) Partan ese contenedor en piezas. Para cada pieza digan: ¿queda en
  el borde (gateway) o detrás? No inventen diez servicios: el mínimo que
  separe borde, logística e (si hace falta) aviso.
Borde(Gateway): JWT, Rate limit Html y ruteo
Detras: Pedidos, recomendar y avisos (Asincrono)

4 — `localhost', la trampa favorita (10 puntos)
═══════════════════════════════════════════════

  Pedidos corre en un contenedor. Recomendar en otro, misma Compose.
  Alguien «arregla» la conexión así:

  ┌────
  │ RECOMENDAR_URL=http://127.0.0.1:8002
  └────

  En su laptop, *sin* Docker, ese `curl' a `127.0.0.1:8002' sí
  funcionaba.

  a) Expliquen por qué en Compose ese arreglo suele fallar *aunque*
  Recomendar esté sano. ¿A qué proceso apunta `127.0.0.1' desde dentro
  de Pedidos?
Cada contenedor tiene su propia red, Dentro de Pedidos, 127.0.0.1 apunta a Pedidos mismo, donde no hay nada  en el 8002, asi que la conexion se rechaza aunque Recomendar este sano
  b) ¿Por qué `http://recomendar:8002' sí tiene chance de funcionar?
  ¿Quién «inventa» el nombre `recomendar'?
Por que compose crea una red con un DNS interno que resuelve los nombres de los servicios, el nombre "recomendar" lo inventa la clave que pusimos en services: del docker-compose.yml, ademas el 8002 tiene que ser el puerto donde escucha adentro el contenedor

  c) Ahora Recomendar se muda a la laptop de otro alumno
  (`192.168.0.57'). Escriban la URL que pondrían *y* dos cosas que
  tienen que ser verdad en la WiFi para que no sea teatro (puertos,
  firewall, etc.). Si solo cambian la URL y nada más, ¿qué puede seguir
  fallando?
La URL seria http://192.168.0.57:8002
Tiene que ser verdad que recomendar escuche en 0.0.0.0 y no en 127.0.0.1 con el puerto 8002 publicado, y que el firewall de la laptop deje entrar al 8002 y que la wifi no aisle a los equipos. Si solo cambian la URL puede seguir dando timeout y lo peor es que pedidos usaria el plan B siempre sin avisar, todo "funciona" pero nunca se usa el modelo

5 — Fallo parcial con números (10 puntos)
═════════════════════════════════════════

  Escenario medido en laboratorio (inventado pero coherente):

  • 1000 `POST /pedidos' por hora en promedio.
  • Recomendar tarda 200 ms cuando está bien.
  • El 5 % del tiempo Recomendar no responde (timeout 3 s).
  • Pedidos, si hay timeout, usa plan B (moto) y responde 200 en 50 ms.
  • El gateway añade 5 ms.

  a) En la hora «normal» (Recomendar bien), ¿el cliente espera ~200 ms o
  ~3 s? ¿Quién pone el tiempo dominante?
Espera como 205 ms, 200 de recomendar mas los 5 del gateway, el que pone el tiempo dominante es recomendar

  b) En el 5 % malo, con plan B: ¿el cliente ve error o pedido creado?
  ¿Qué «mentira útil» están aceptando (medio quizá no óptimo)?
El cliente ve el pedido creado, pero tarda como 3.05 s por que primero espera el timeout de 3 s y luego ya usa la moto. La mentira util es aceptar la moto aunque no sea el mejor medio, a cambio de no perder el pedido. Ese 5% sube el promedio a como 348 ms

  c) Un compañero dice: «Mejor que Pedidos *reintente* 10 veces hasta
  que Recomendar vuelva; así nunca usamos plan B.» ¿Qué le pasa a la
  cola de peticiones y al gateway si Recomendar está caído 10 minutos?
  ¿Plan B siempre es peor que reintentar? Argumenten.
Si reintenta 10 veces de 3 s son 30 s por pedido, en 10 minutos se juntan como 167 peticiones ocupando workers, pedidos se satura y el gateway empieza a dar timeout (504), y cuando recomendar regresa le cae una avalancha de reintentos que lo puede volver a tumbar. Como vimos en clase los reintentos van con tope y circuit breaker. Pero el plan B no siempre es mejor, si un medio equivocado sale caro o es peligroso es mejor dejar el pedido como pendiente que inventar el medio

6 — Apagan el «edificio equivocado» (10 puntos)
═══════════════════════════════════════════════

  Tres contenedores: gateway, pedidos, recomendar. Hacen tres
  experimentos *por separado*:

  1. `docker compose stop gateway'
  2. `docker compose stop pedidos'
  3. `docker compose stop recomendar'

  Para *cada* experimento digan qué ve el navegador en `http://IP:8080/'
  (página / crear pedido) y qué sigue vivo por dentro. No basta «no
  jala»: digan *qué* no jala y qué sí podría seguir respondiendo si
  alguien hablara por dentro de la red.

  Luego: ¿en cuál de los tres el sistema «parece» más muerto hacia
  afuera aunque más piezas sigan arriba? ¿Qué les enseña eso del borde?
1.- Stop gateway: el navegador no conecta, no hay pagina ni pedidos, pero por dentro pedidos y recomendar siguen vivos y responden dentro de la red
2.- Stop pedidos: la pagina si carga por que el gateway da el HTML, pero crear pedido da error 502, recomendar sigue vivo pero nadie lo usa
3.- Stop recomendar: la pagina carga y el pedido se crea con plan B (moto), y rapido por que la conexion se rechaza luego luego
El que parece mas muerto es el 1 aunque 2 de 3 servicios siguen arriba, eso enseña que el borde es el punto unico de falla, hay que tenerlo simple y con respaldo


7 — WiFi del salón, conflicto de roles (10 puntos)
══════════════════════════════════════════════════

  Cuatro alumnos:

  • Ana: gateway + HTML
  • Beto: pedidos
  • Carla: recomendar
  • Diana: «yo también levanté un gateway en mi laptop por si Ana falla»

  Todos en la misma WiFi. El cliente (otro equipo) configura a veces la
  IP de Ana y a veces la de Diana.

  a) ¿Qué problema de *diseño* introdujo Diana aunque «todo responda
  200»? (Piensen en una sola puerta vs dos puertas.)
Diana hizo dos puertas, las reglas de autenticacion y limites pueden quedar diferentes en cada una, los logs quedan partidos y el cliente tiene que adivinar que IP usar. El respaldo es buena idea pero detras de una sola direccion o un balanceador, no con el cliente cambiando IPs

  b) Beto configuró `RECOMENDAR_URL=http://localhost:8002' porque en su
  máquina desarrolló Pedidos y Recomendar juntos. En el salón Recomendar
  está en la laptop de Carla. ¿Qué falla y cómo lo corrigen *sin* juntar
  otra vez los dos servicios en la laptop de Beto?
localhost en la laptop de Beto apunta a su propia maquina y ahi no hay recomendar, entonces todo cae al plan B. Se corrige poniendo RECOMENDAR_URL=http://IP_de_Carla:8002 como variable de entorno sin tocar el codigo, y Carla tiene que escuchar en 0.0.0.0 y abrir el puerto en el firewall

  c) La WiFi del campus aísla clientes («AP isolation»). `ping' entre
  alumnos falla. ¿Pueden hacer la práctica tal cual? Si no, propongan
  *un* plan B de laboratorio que preserve la lección «procesos
  separados» (aunque no sea WiFi del salón).
Tal cual no se puede por que con AP isolation no se ven entre ellos. El plan B seria un router portatil o el hotspot de un celular sin aislamiento y conectar las 4 laptops ahi, asi se sigue viendo lo de procesos separados en maquinas distintas


8 — El front que conoce demasiado (10 puntos)
═════════════════════════════════════════════

  El HTML hace esto al enviar el formulario:

  ┌────
  │ await fetch("http://192.168.1.20:8002/sugerir", { ... }); // Recomendar
  │ await fetch("http://192.168.1.30:8001/pedidos", { ... }); // Pedidos
  └────

  El autor dice: «Más rápido: me salto el gateway.»

  a) Listen *tres* problemas (seguridad, cambio de IP, orden de
  llamadas, consistencia del folio, CORS, etc.).
1.- Expone las IPs internas y cualquiera puede llamar a recomendar o pedidos sin autenticacion
2.- Si cambia una IP hay que cambiar el JS de todos los clientes
3.- Si la segunda llamada falla queda una recomendacion huerfana, y el cliente puede cambiar el medio entre las dos llamadas, ademas sale el problema de CORS con dos origenes

  b) Rediseñen la secuencia correcta con gateway: *una* llamada desde el
  navegador. ¿Quién habla con Recomendar y por qué no el navegador?
El navegador hace un solo POST /api/pedidos al gateway, el gateway lo pasa a pedidos, pedidos llama a recomendar, guarda el pedido con folio y la respuesta regresa por el gateway. Recomendar lo llama pedidos por que elegir el medio es logica del servidor y el navegador no es confiable

  c) El selector de modelo (`arbol=|=bosque=|=red') va en el JSON. Si el
  front llama directo a Recomendar *y* a Pedidos, ¿quién debería crear
  el folio para no duplicar lógica? ¿Qué invariante rompen si los dos
  «crean» algo?
El folio lo crea pedidos, recomendar solo recibe datos y regresa una sugerencia sin guardar nada. El selector de modelo va en el JSON hacia pedidos y pedidos se lo pasa a recomendar. La invariante es un pedido = un folio con el medio que calculo el servidor, si los dos crean algo salen folios duplicados o que no cuadran


9 — El LLM vendedor (10 puntos)
═══════════════════════════════

  Producto: tienda + envíos.

  • Modelo `.joblib': medio de transporte.
  • LLM: texto para convencer al cliente en la ficha del producto.

  Un arquitecto propone *un solo* microservicio `cerebro' que: recibe el
  carrito, elige el medio con el árbol *y* genera el pitch de ventas con
  el LLM, todo en la misma petición `/inteligente'.

  a) Critiquen el nombre y el corte. ¿Qué dos oficios distintos
  mezclaron? ¿Qué falla cuando el LLM tarda 8 s y el despacho necesita
  responder en < 500 ms?
"Cerebro" describe la tecnologia no el negocio. Mezcla logistica que es un modelo rapido y critico con marketing que es un LLM lento, caro y no critico. Si el LLM tarda 8 s el despacho ya no cumple sus 500 ms, y si el LLM se cae se cae el despacho tambien

  b) Propongan dos endpoints (o dos servicios) y digan cuál usa el
  *front de tienda* y cuál el *flujo de pedido/envío*.
POST /logistica/medio lo usa el flujo de pedido y envió
GET /ventas/pitch?producto=... lo usa el front de la tienda, con cache y un texto generico si falla

  c) El LLM vive en un server con GPU en otra red. El front de tienda
  ¿apunta a la GPU o al gateway? Si mañana cambian de proveedor LLM
  (otro host), ¿qué archivo/config quieren tocar *una sola vez*?
El front apunta al gateway nunca a la GPU. Si cambian de proveedor solo se cambia la variable LLM_URL en la config del servicio de ventas y el front ni se entera


10 — El inversionista y la semana imposible (10 puntos)
═══════════════════════════════════════════════════════

  Hoy:

  • Panel interno: monolito Django (funciona, poco tráfico).
  • App clientes: gateway + pedidos + recomendar.
  • Idea: LLM de ventas (aún no).
  • Equipo: 5 personas.
  • Inversionista: «Todo a microservicios en 7 días, incluido el panel,
    o no hay dinero.»

  a) Escriban la respuesta al inversionista (máx. 8 líneas) con postura
  *y* riesgo concreto si obedecen a ciegas.
Si a microservicios pero donde duelen. La app de clientes ya esta separada, el panel funciona y tiene poco trafico, partirlo en 7 dias con 5 personas no da dinero ni estabilidad. El riesgo es que una migracion apurada tumbe pedidos en produccion y perdamos clientes. Esta semana proponemos asegurar el gateway y aislar el reentrenamiento, y medir cuando si vale la pena partir el panel

  b) Ordenen *estas cuatro* iniciativas de más a menos urgente para
  *esta* semana y justifiquen el orden (no el catálogo soñado):

  1. Partir el panel Django en 6 microservicios.
  2. Sacar el reentrenamiento del `.joblib' a un pipeline que no tumbe
     Pedidos.
  3. Meter auth + rate limit en el gateway público.
  4. Subir el LLM de ventas a producción sin timeouts ni plan B.
1.- (3) Auth y rate limit en el gateway, por que ya esta expuesto y es barato hacerlo
2.- (2) Pipeline de reentrenamiento, por que hoy tumba pedidos cada semana
3.- (4) LLM, pero solo con timeout y plan B, como esta planteado no se sube
4.- (1) Partir el panel, funciona y tiene poco trafico asi que no es urgente


  c) Inventen *una* métrica que les diga «ya toca partir X del monolito»
  (no «porque está de moda»). Tiene que ser observable (tiempo, errores,
  despliegues, equipo…).
El % de despliegues del monolito que se bloquean o se revierten por cambios en el modulo X, si pasa del 30% durante un mes ya toca partir X

  d) Cierren con una frase propia (no copien el apunte) que capture:
  ¿microservicios son el objetivo o la herramienta?
Los microservicios son una herramienta, se parte el sistema cuando un limite duele no por que este de moda
