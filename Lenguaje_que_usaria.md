# ¿Qué lenguaje usaría? — Propuestas de sistemas

**Nombre:** Rodrigo Vega Espinoza
**Matrícula:** 22121334
**Fecha:** 28/08/2026

---

## 1. Mensajería tipo WhatsApp sobre LoRa

**Idea:** mandar mensajes de texto sin internet ni señal celular (en la sierra, en un rancho, después de un sismo). Cada persona trae un módulo LoRa (ESP32 + radio SX1276) y su celular se conecta al módulo por Bluetooth.

### Lenguajes

| Parte | Lenguaje | Por qué |
|---|---|---|
| Firmware del módulo | **C++** (framework Arduino + librería RadioLib) | El ESP32 tiene poca memoria y hay que controlar directamente el radio, los tiempos de espera y el modo de bajo consumo. C++ da ese control sin cargar un intérprete. MicroPython sería más fácil de escribir, pero gasta RAM y batería que aquí sí importan. |
| App del celular | **Kotlin** (Android nativo) | Lo crítico de la app es el Bluetooth y que siga recibiendo mensajes con la pantalla apagada. Eso se hace con un *foreground service* de Android, y en nativo es más confiable que a través de un framework multiplataforma. Además, en las zonas sin señal donde se usaría casi todos tienen Android, así que iOS no es prioridad para una primera versión. |

### Patrones

- **Observer:** el servicio de Bluetooth avisa a la pantalla del chat cuando llega un mensaje, en vez de que la app pregunte cada segundo si hay algo nuevo.
- **Command + cola (store-and-forward):** cada mensaje enviado se guarda como un objeto en una cola local con su id. LoRa pierde paquetes y a veces el otro nodo no está en alcance, así que el mensaje se reintenta hasta recibir confirmación (ACK). Con el id, el que recibe descarta los duplicados.

### Lo que hay que cuidar

LoRa manda pocos bytes por paquete (alrededor de 200) y la ley limita cuánto tiempo puede transmitir cada equipo. Por eso los mensajes deben ser cortos y sin fotos, y el protocolo tiene que ser binario y compacto, no JSON.

---

## 2. Detección de cajones libres en un estacionamiento con cámaras

**Idea:** usar las cámaras que ya existen para saber qué cajones están libres y mostrarlo en una app o en una pantalla en la entrada.

### Lenguajes

| Parte | Lenguaje | Por qué |
|---|---|---|
| Detección (junto a las cámaras) | **Python** con OpenCV y un modelo YOLO pequeño | Todas las herramientas de visión ya existen en Python: leer el video RTSP de la cámara, detectar autos y dibujar los cajones. Escribir esto en otro lenguaje sería rehacer lo que ya está hecho. El modelo pesado lo corre la librería en C/CUDA por debajo, así que Python solo coordina. |
| API para la app | **Python con Django** (o FastAPI) | Expone `GET /cajones` con el estado de cada uno en JSON. Así se mantiene un solo lenguaje en todo el servidor. |

Lo correría **en el estacionamiento** (una mini PC con GPU o una Jetson), no en la nube: mandar el video de todas las cámaras a internet todo el día cuesta mucho ancho de banda, y el estado de un cajón pesa unos cuantos bytes.

### Patrones

- **Pipes and Filters (tubería):** cada cuadro del video pasa por pasos separados: leer cuadro → detectar autos → cruzar con el mapa de cajones → actualizar estado. Cada paso se puede cambiar solo (por ejemplo, otro modelo de detección) sin tocar los demás.
- **State:** cada cajón tiene estados `libre`, `ocupado` y `en duda`. No cambia de libre a ocupado con un solo cuadro, sino después de varios segundos seguidos. Así una persona caminando o un auto que va pasando no hacen que el cajón "parpadee".
- **Observer / publicar-suscribir:** solo cuando un cajón cambia de estado se avisa a la API y a la pantalla de la entrada. No se manda el estado completo 30 veces por segundo.

### Lo que hay que cuidar

De noche, con lluvia o con un poste tapando la vista, la detección falla. Por eso conviene el estado `en duda` en lugar de inventar que el cajón está libre. Además, el video de las cámaras no debe guardarse ni salir del lugar, porque se ven personas y placas.
