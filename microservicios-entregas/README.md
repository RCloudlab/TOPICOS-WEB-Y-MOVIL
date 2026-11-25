# microservicios-entregas

Tres contenedores: **gateway** (nginx, puerto 8080) → **pedidos** (Flask, sin scikit-learn) → **recomendar** (Flask + `.joblib` + reglas).

```
Navegador ──► gateway :8080 ──/pedidos──► pedidos :5000 ──POST /sugerir──► recomendar :5001
                    ├── /              → html/index.html
                    ├── /salud/pedidos
                    └── /salud/recomendar
```

## Correr

```bash
# (una vez) copiar el Random Forest, que no se sube a GitHub por su tamaño
cp ../plataforma-entregas/entregas/modelo/modelo_bosque.joblib recomendar/ia/modelo/

docker compose up -d --build
docker compose ps
```

Abrir http://localhost:8080

```bash
curl -X POST localhost:8080/pedidos -H "Content-Type: application/json" --data-binary @paquete.json
curl localhost:8080/pedidos/PED-00001
docker compose stop recomendar     # pedidos sigue vivo y responde 202 "pendiente_de_medio"
docker compose start recomendar
```

## Servicios

| Servicio | Rutas | Qué hace |
|---|---|---|
| recomendar | `GET /salud`, `POST /sugerir` | Carga árbol / bosque / red, aplica `reglas.es_posible` y regresa medio, ranking y descartados. No crea folios. |
| pedidos | `GET /salud`, `POST /pedidos`, `GET /pedidos/<folio>` | Crea el folio, llama a `RECOMENDAR_URL` con timeout y arma el plan con `medios.crear_medio()`. Si recomendar falla, guarda el pedido sin medio (202). |
| gateway | `/`, `/pedidos`, `/salud/*` | Sirve la página y enruta. recomendar solo se expone por `/salud/recomendar`. |

`ia/recomendador.py`, `ia/reglas.py` y `pedidos/medios.py` vienen de mi `plataforma-entregas` (Django) sin cambios.

La salida de las pruebas está en `evidencias/`.
