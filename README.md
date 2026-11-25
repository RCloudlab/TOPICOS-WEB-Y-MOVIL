# Tópicos Selectos de Tecnologías Web y Móvil

**Alumno:** Rodrigo Vega Espinoza · **Matrícula:** 22121334 · **Equipo:** 3
**Profesor:** Jesús Eduardo Alcaraz Chávez · Instituto Tecnológico de Morelia · Ago–Dic 2026

Apuntes del curso: <https://ealcaraz85.github.io/topicoswebmobil/>
Proyectos 1 y 2 (KitAte, artículos deportivos): <https://github.com/RCloudlab/KitAte>

---

## Actividades

| Fecha | Actividad | Entrega |
|---|---|---|
| 27/08/2026 | Examen diagnóstico 2 | [Examen_Diagnostico2.md](Examen_Diagnostico2.md) |
| 28/08/2026 | ¿Qué lenguaje usaría? Mensajería LoRa y estacionamiento con cámaras | [Lenguaje_que_usaria.md](Lenguaje_que_usaria.md) |
| 31/08/2026 | 20 lenguajes: paradigmas y patrones de diseño | [Reporte_Lenguajes_Patrones_de_Diseno.md](Reporte_Lenguajes_Patrones_de_Diseno.md) |
| 02/09/2026 | Misiones 1 y 2: patrones del portal universitario | [patrones-portal-universitario.md](patrones-portal-universitario.md) |
| 03/09/2026 | Auditoría del portal universitario | [informe_auditoria.md](informe_auditoria.md) |
| 24–28/09/2026 | Cinco días: plataforma de entregas en Django | [Día 1](Dia%201) · [Día 2](Dia2/) · [Día 3](Dia3/) · [Día 4](Dia4/) · [Día 5 + README](Dia5/README.md) |
| 08/10/2026 | Lo que hay detrás de la implementación | [actividades/implementacion/](actividades/implementacion/22121334_vega.md) |
| 20/10/2026 | Análisis de envios-data (6 archivos vs el árbol) | [actividades/analisis-envios-data/](actividades/analisis-envios-data/ANALISIS_ENVIOS.md) |
| 26/10/2026 | Monolito con API frente a microservicios | [actividades/arquitectura/](actividades/arquitectura/22121334_vega.md) |
| 28/10/2026 | Microservicios con Docker (código + reporte) | [microservicios-entregas/](microservicios-entregas/README.md) · [reporte](actividades/microservicios-docker/22121334_vega.md) |
| 03/11/2026 | Examen: microservicios, gateway y el monolito con API | [examen_microservicios_gateway_Rodrigo_Vega.md](examen_microservicios_gateway_Rodrigo_Vega.md) |
| 05/11/2026 | Flutter: fundamentos, instalación y widgets | [flutter-fundamentos/](flutter-fundamentos/FLUTTER_FUNDAMENTOS.md) |
| 24/11/2026 | Auditar el proyecto (KitAte) con IA libre | [actividades/auditoria-ia/](actividades/auditoria-ia/AUDITORIA_KITATE.md) |

La actividad RAG (corpus para el asistente) va en el repo de [KitAte](https://github.com/RCloudlab/KitAte).

---

## Cómo correr lo que tiene código

| Carpeta | Comandos |
|---|---|
| `Dia5/` (Django) | `python -m venv .venv` → `.venv\Scripts\activate` → `pip install Django` → `python manage.py migrate` → `python manage.py runserver` · pruebas: `python manage.py test` |
| `microservicios-entregas/` | `docker compose up -d --build` → abrir <http://localhost:8080> (ver su README para copiar el Random Forest) |
| `flutter-fundamentos/app/` | `flutter pub get` → `flutter run -d chrome` · pruebas: `flutter test` |
| `actividades/analisis-envios-data/` | `python analizar_envios.py datos resultados_envios` · `python evaluar_modelo.py <modelo.joblib> datos` |
| `actividades/auditoria-ia/` | Con Ollama corriendo: `python correr_auditoria.py <ruta_a_KitAte> llama3.2 qwen2.5-coder:7b` |
