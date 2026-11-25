# Paquete de contexto: KitAte
Archivos clave del proyecto. Secretos reemplazados por <OMITIDO>.

## backend/tienda/settings.py
```python
# Configuración general del proyecto Django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = '<OMITIDO: secreto>'

# Modo desarrollo; se permite el emulador Android (10.0.2.2)
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "10.0.2.2", "*"] if DEBUG else []


# Apps de Django y apps propias del proyecto
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalogo',
    'pedidos',
    'recomendador',
    'asistente',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tienda.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tienda.wsgi.application'


# Base de datos SQLite local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Idioma y zona horaria de México
LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

## backend/tienda/urls.py
```python
# Rutas principales: todas las APIs cuelgan de /api/
from django.contrib import admin
from django.urls import include, path

# Front Controller: Django recibe todo y reparte a cada app
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("catalogo.urls")),
    path("api/", include("recomendador.urls")),
    path("api/", include("pedidos.urls")),
    path("api/", include("asistente.urls")),
]
```

## backend/requirements.txt
```text
asgiref==3.12.1
cloudpickle==3.1.2
Django==5.2.17
joblib==1.6.0
narwhals==2.27.1
numpy==2.5.4
pandas==3.0.6
python-dateutil==2.9.0.post0
scikit-learn==1.9.0
scipy==1.18.1
six==1.17.0
sqlparse==0.6.0
threadpoolctl==3.7.0
```

## backend/catalogo/models.py
```python
# Modelo de productos del catálogo y sus opciones fijas
from django.db import models

# Opciones de nivel, deporte y tipo de producto
NIVELES = [
    ("INICIACION", "Iniciación"),
    ("RECREATIVO", "Recreativo"),
    ("INTERMEDIO", "Intermedio"),
    ("COMPETITIVO", "Competitivo"),
]

DEPORTES = [
    ("running", "Running"),
    ("ciclismo", "Ciclismo"),
    ("gimnasio", "Gimnasio"),
    ("futbol", "Fútbol"),
    ("natacion", "Natación"),
    ("yoga", "Yoga"),
    ("general", "General (cualquier deporte)"),
]

TIPOS = [
    ("calzado", "Calzado"),
    ("ropa", "Ropa"),
    ("equipo", "Equipo"),
    ("accesorio", "Accesorio"),
    ("recuperacion", "Recuperación"),
    ("monitoreo", "Monitoreo"),
    ("proteccion", "Protección"),
]


# Producto deportivo que se guarda en la base de datos
class Producto(models.Model):
    sku = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    deporte = models.CharField(max_length=20, choices=DEPORTES)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    nivel = models.CharField(max_length=20, choices=NIVELES)
    marca = models.CharField(max_length=40)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen_url = models.URLField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["deporte", "tipo", "precio"]

    def __str__(self):
        return f"{self.sku} · {self.nombre}"

    # Convierte el producto a diccionario para la respuesta JSON
    def a_dict(self, detalle=False):
        datos = {
            "id": self.id,
            "sku": self.sku,
            "nombre": self.nombre,
            "deporte": self.deporte,
            "tipo": self.tipo,
            "nivel": self.nivel,
            "marca": self.marca,
            "precio": float(self.precio),
            "stock": self.stock,
            "imagen_url": self.imagen_url,
        }
        if detalle:
            datos["descripcion"] = self.descripcion
            datos["deporte_nombre"] = self.get_deporte_display()
            datos["tipo_nombre"] = self.get_tipo_display()
            datos["nivel_nombre"] = self.get_nivel_display()
        return datos
```

## backend/catalogo/repositories.py
```python
# Repositorio: consultas de productos a la base de datos
from django.db.models import Q

from .models import NIVELES, Producto

ORDEN_NIVELES = [clave for clave, _ in NIVELES]


# Patrón Repository: aísla las consultas del ORM de las vistas
class ProductoRepository:
    # Solo productos activos
    def _activos(self):
        return Producto.objects.filter(activo=True)

    # Busca productos por texto y filtros opcionales
    def buscar(self, texto="", deporte="", tipo="", nivel=""):
        consulta = self._activos()
        if texto:
            consulta = consulta.filter(
                Q(nombre__icontains=texto)
                | Q(marca__icontains=texto)
                | Q(descripcion__icontains=texto)
                | Q(sku__icontains=texto)
            )
        if deporte:
            consulta = consulta.filter(deporte=deporte)
        if tipo:
            consulta = consulta.filter(tipo=tipo)
        if nivel:
            consulta = consulta.filter(nivel=nivel)
        return list(consulta)

    # Busca un producto activo por su id
    def por_id(self, producto_id):
        return self._activos().filter(id=producto_id).first()

    # Regresa un diccionario id -> producto
    def por_ids(self, ids):
        return {p.id: p for p in self._activos().filter(id__in=ids)}

    # Busca productos con stock bajando de nivel si no hay
    def candidatos(self, deporte, tipo, nivel):
        indice = ORDEN_NIVELES.index(nivel)
        for nivel_buscado in reversed(ORDEN_NIVELES[: indice + 1]):
            # Primero el deporte pedido y luego los generales
            for deporte_buscado in (deporte, "general"):
                encontrados = list(
                    self._activos().filter(
                        deporte=deporte_buscado, tipo=tipo,
                        nivel=nivel_buscado, stock__gt=0,
                    )
                )
                if encontrados:
                    return encontrados
        return []
```

## backend/catalogo/views.py
```python
# Vistas de la API del catálogo (listar y ver detalle)
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .repositories import ProductoRepository

repositorio = ProductoRepository()


# Lista productos con filtros opcionales por texto, deporte, tipo y nivel
@require_GET
def lista_productos(request):
    productos = repositorio.buscar(
        texto=request.GET.get("q", "").strip(),
        deporte=request.GET.get("deporte", ""),
        tipo=request.GET.get("tipo", ""),
        nivel=request.GET.get("nivel", ""),
    )
    return JsonResponse(
        {"total": len(productos), "productos": [p.a_dict() for p in productos]},
        json_dumps_params={"ensure_ascii": False},
    )


# Devuelve un producto por id o 404 si no existe
@require_GET
def detalle_producto(request, producto_id):
    producto = repositorio.por_id(producto_id)
    if producto is None:
        return JsonResponse({"error": "producto no encontrado"}, status=404)
    return JsonResponse(producto.a_dict(detalle=True), json_dumps_params={"ensure_ascii": False})
```

## backend/recomendador/validacion.py
```python
# Valida el perfil que manda la app y calcula IMC y horas
DEPORTES = ["running", "ciclismo", "gimnasio", "futbol", "natacion", "yoga"]
OBJETIVOS = ["salud", "bajar_peso", "rendimiento", "competencia"]

# Rangos permitidos para cada campo numérico
RANGOS = {
    "edad": (10, 100),
    "dias_semana": (0, 7),
    "minutos_sesion": (0, 300),
    "anios_experiencia": (0, 80),
    "peso_kg": (25, 250),
    "estatura_cm": (100, 230),
    "presupuesto_mxn": (1, 200000),
}
OBLIGATORIOS = list(RANGOS) + ["lesion_reciente", "deporte", "objetivo"]


# Error con mensaje y detalle para regresar un 400
class ErrorValidacion(Exception):
    def __init__(self, mensaje, detalle=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.detalle = detalle or {}


# Convierte valores como 'si' o 1 a booleano
def _a_bool(valor):
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, (int, float)):
        return valor != 0
    return str(valor).strip().lower() in ("1", "true", "si", "sí", "yes")


# Revisa campos y rangos, y regresa el perfil listo para el modelo
def validar_perfil(cuerpo: dict) -> dict:
    faltantes = [c for c in OBLIGATORIOS if c not in cuerpo or cuerpo[c] in ("", None)]
    if faltantes:
        raise ErrorValidacion("faltan campos", {"campos": faltantes})

    errores = {}
    numeros = {}
    for campo, (minimo, maximo) in RANGOS.items():
        try:
            valor = float(cuerpo[campo])
        except (TypeError, ValueError):
            errores[campo] = "debe ser un número"
            continue
        if not minimo <= valor <= maximo:
            errores[campo] = f"debe estar entre {minimo} y {maximo}"
        numeros[campo] = valor

    deporte = str(cuerpo["deporte"]).strip().lower()
    objetivo = str(cuerpo["objetivo"]).strip().lower()
    if deporte not in DEPORTES:
        errores["deporte"] = f"opciones: {', '.join(DEPORTES)}"
    if objetivo not in OBJETIVOS:
        errores["objetivo"] = f"opciones: {', '.join(OBJETIVOS)}"
    if errores:
        raise ErrorValidacion("datos inválidos", {"errores": errores})

    estatura_m = numeros["estatura_cm"] / 100
    dias = int(numeros["dias_semana"])
    minutos = int(numeros["minutos_sesion"])
    return {
        "edad": int(numeros["edad"]),
        "dias_semana": dias,
        "minutos_sesion": minutos,
        "horas_semana": round(dias * minutos / 60, 2),
        "anios_experiencia": round(numeros["anios_experiencia"], 1),
        "imc": round(numeros["peso_kg"] / (estatura_m ** 2), 1),
        "lesion_reciente": int(_a_bool(cuerpo["lesion_reciente"])),
        "presupuesto_mxn": round(numeros["presupuesto_mxn"], 2),
        "deporte": deporte,
        "objetivo": objetivo,
        "peso_kg": numeros["peso_kg"],
        "estatura_cm": numeros["estatura_cm"],
    }
```

## backend/recomendador/reglas.py
```python
# Reglas de seguridad y negocio que descartan niveles no aptos
from abc import ABC, abstractmethod
from typing import Callable

NIVELES = ["INICIACION", "RECREATIVO", "INTERMEDIO", "COMPETITIVO"]
NIVEL_RESPALDO = "INICIACION"


# Posición del nivel, para comparar de menor a mayor
def orden(nivel: str) -> int:
    return NIVELES.index(nivel)


# Base de las reglas: regresa la razón o None si pasa
class Regla(ABC):
    nombre = "regla"

    @abstractmethod
    def revisar(self, nivel: str, perfil: dict) -> str | None:
        pass


# Si no entrena ningún día solo puede ser INICIACION
class ReglaSinActividad(Regla):
    nombre = "sin_actividad"

    def revisar(self, nivel, perfil):
        if perfil["dias_semana"] == 0 and nivel != "INICIACION":
            return "no entrena ningún día a la semana: se empieza por INICIACION"
        return None


# Con lesión reciente el máximo es RECREATIVO
class ReglaLesion(Regla):
    nombre = "lesion_reciente"
    MAXIMO = "RECREATIVO"

    def revisar(self, nivel, perfil):
        if perfil["lesion_reciente"] and orden(nivel) > orden(self.MAXIMO):
            return "lesión reciente: máximo RECREATIVO hasta tener alta médica"
        return None


# COMPETITIVO solo entre 16 y 64 años
class ReglaEdadCompetitiva(Regla):
    nombre = "edad_competitiva"
    EDAD_MIN = 16
    EDAD_MAX = 64

    def revisar(self, nivel, perfil):
        if nivel != "COMPETITIVO":
            return None
        if perfil["edad"] < self.EDAD_MIN:
            return f"menor de {self.EDAD_MIN} años: no se sugiere kit COMPETITIVO"
        if perfil["edad"] > self.EDAD_MAX:
            return f"mayor de {self.EDAD_MAX} años: COMPETITIVO requiere valoración médica"
        return None


# COMPETITIVO pide días mínimos y años de experiencia
class ReglaBaseCompetitiva(Regla):
    nombre = "base_competitiva"
    DIAS_MIN = 4
    ANIOS_MIN = 2

    def revisar(self, nivel, perfil):
        if nivel != "COMPETITIVO":
            return None
        if perfil["dias_semana"] < self.DIAS_MIN:
            return f"COMPETITIVO requiere entrenar al menos {self.DIAS_MIN} días"
        if perfil["anios_experiencia"] < self.ANIOS_MIN:
            return f"COMPETITIVO requiere al menos {self.ANIOS_MIN} años de experiencia"
        return None


# El kit más barato del nivel debe caber en el presupuesto
class ReglaPresupuesto(Regla):
    nombre = "presupuesto"

    def __init__(self, costo_minimo: Callable[[str, dict], float]):
        self._costo_minimo = costo_minimo

    def revisar(self, nivel, perfil):
        if nivel == NIVEL_RESPALDO:
            return None
        costo = self._costo_minimo(nivel, perfil)
        if costo > perfil["presupuesto_mxn"]:
            return (
                f"el kit {nivel} más económico cuesta ${costo:,.0f} y el "
                f"presupuesto es ${perfil['presupuesto_mxn']:,.0f}"
            )
        return None


# Lista de reglas que usa el recomendador
def reglas_por_defecto(costo_minimo: Callable[[str, dict], float]) -> list[Regla]:
    return [
        ReglaSinActividad(),
        ReglaLesion(),
        ReglaEdadCompetitiva(),
        ReglaBaseCompetitiva(),
        ReglaPresupuesto(costo_minimo),
    ]


# Junta las razones por las que un nivel queda descartado
def revisar_nivel(nivel: str, perfil: dict, reglas: list[Regla]) -> list[dict]:
    razones = []
    for regla in reglas:
        razon = regla.revisar(nivel, perfil)
        if razon:
            razones.append({"regla": regla.nombre, "razon": razon})
    return razones
```

## backend/recomendador/recomendador.py
```python
# Carga el modelo .joblib y saca el nivel aplicando las reglas
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from .reglas import NIVEL_RESPALDO, Regla, orden, revisar_nivel

CARPETA_MODELOS = Path(__file__).resolve().parent / "modelo"

# Modelos disponibles y su archivo .joblib
MODELOS = {
    "arbol": {
        "archivo": "modelo_nivel_arbol.joblib",
        "nombre": "Árbol de decisión",
        "etiqueta_motivo": "árbol de decisión",
    },
    "bosque": {
        "archivo": "modelo_nivel_bosque.joblib",
        "nombre": "Random Forest",
        "etiqueta_motivo": "random forest",
    },
}

# Columnas que espera el modelo, en el mismo orden del entrenamiento
CAMPOS_NUMERICOS = [
    "edad", "dias_semana", "minutos_sesion", "horas_semana", "anios_experiencia",
    "imc", "lesion_reciente", "presupuesto_mxn",
]
CAMPOS_TEXTO = ["deporte", "objetivo"]
CAMPOS = CAMPOS_NUMERICOS + CAMPOS_TEXTO


# Resultado completo que se manda a la app
@dataclass
class ResultadoRecomendacion:
    nivel: str
    confianza: float
    motivo: str
    modelo: str
    modelo_nombre: str
    preferido_por_modelo: str
    confianza_modelo: float
    corregido_por_reglas: bool
    ranking: list
    descartados: list
    proceso: list = field(default_factory=list)

    def a_dict(self):
        return asdict(self)


# Interfaz común del recomendador (Adapter sobre el modelo)
class RecomendadorIA(ABC):
    @abstractmethod
    def explicar(self, perfil: dict, reglas: list[Regla]) -> ResultadoRecomendacion:
        pass


# Adapter: envuelve el modelo de sklearn guardado en .joblib
class RecomendadorSklearn(RecomendadorIA):

    def __init__(self, clave: str):
        if clave not in MODELOS:
            raise ValueError(f"modelo desconocido: {clave}")
        info = MODELOS[clave]
        ruta = CARPETA_MODELOS / info["archivo"]
        if not ruta.exists():
            raise FileNotFoundError(
                f"No encuentro {ruta}. Entrene el modelo (carpeta ml/) y cópielo "
                "a recomendador/modelo/."
            )
        self.clave = clave
        self.nombre = info["nombre"]
        self.etiqueta_motivo = info["etiqueta_motivo"]
        self._modelo = joblib.load(ruta)

    # Predice, ordena los niveles y descarta los que rompen reglas
    def explicar(self, perfil, reglas):
        proceso = [
            {
                "paso": 1,
                "titulo": "Perfil recibido",
                "detalle": "La vista valida los campos y calcula el IMC; el adaptador "
                           "arma un DataFrame de una fila.",
            },
            {
                "paso": 2,
                "titulo": f"El modelo ({self.nombre}) calcula probabilidades",
                "detalle": "predict_proba responde un porcentaje por cada nivel. "
                           "Todavía no se elige nada definitivo.",
            },
        ]

        # Probabilidad por nivel y ranking de mayor a menor
        datos = pd.DataFrame([perfil], columns=CAMPOS)
        probabilidades = self._modelo.predict_proba(datos)[0]
        pares = [
            {"nivel": nivel, "confianza": round(float(p), 3)}
            for nivel, p in zip(self._modelo.classes_, probabilidades)
        ]
        preferido = max(pares, key=lambda item: item["confianza"])["nivel"]
        ranking = sorted(
            pares,
            key=lambda item: (
                -item["confianza"],
                abs(orden(item["nivel"]) - orden(preferido)),
                orden(item["nivel"]),
            ),
        )
        confianza_modelo = ranking[0]["confianza"]

        proceso.append({
            "paso": 3,
            "titulo": "Ranking del modelo",
            "detalle": f"Prefiere {preferido} ({confianza_modelo:.0%}). "
                       "Los demás niveles quedan como alternativas.",
            "ranking": ranking,
        })

        # Se recorre el ranking y se queda el primer nivel apto
        descartados = []
        elegido = None
        confianza_elegida = 0.0
        for item in ranking:
            razones = revisar_nivel(item["nivel"], perfil, reglas)
            if not razones:
                elegido = item["nivel"]
                confianza_elegida = item["confianza"]
                break
            descartados.append({
                "nivel": item["nivel"],
                "confianza": item["confianza"],
                "razones": razones,
            })

        proceso.append({
            "paso": 4,
            "titulo": "Las reglas filtran lo no apto",
            "detalle": "Se descarta cualquier nivel que rompa reglas de seguridad "
                       "(edad, lesión, días de entrenamiento, experiencia) o de "
                       "negocio (presupuesto contra el kit más barato del catálogo).",
            "descartados": descartados,
        })

        # Si ninguno pasa, se usa el nivel de respaldo
        if elegido is None:
            elegido = NIVEL_RESPALDO
            confianza_elegida = next(
                i["confianza"] for i in ranking if i["nivel"] == NIVEL_RESPALDO
            )
            motivo = f"ningún nivel sugerido era apto; se usa {NIVEL_RESPALDO}"
            corregido = True
        else:
            motivo = f"{self.etiqueta_motivo}, confianza {confianza_elegida:.0%}"
            corregido = elegido != preferido
            if corregido:
                motivo += f"; se descartó {preferido} por las reglas"

        proceso.append({
            "paso": 5,
            "titulo": "Nivel sugerido",
            "detalle": motivo,
            "nivel": elegido,
            "corregido_por_reglas": corregido,
        })

        return ResultadoRecomendacion(
            nivel=elegido,
            confianza=confianza_elegida,
            motivo=motivo,
            modelo=self.clave,
            modelo_nombre=self.nombre,
            preferido_por_modelo=preferido,
            confianza_modelo=confianza_modelo,
            corregido_por_reglas=corregido,
            ranking=ranking,
            descartados=descartados,
            proceso=proceso,
        )


# Lista de modelos y si su archivo ya existe
def modelos_disponibles():
    return [
        {
            "id": clave,
            "nombre": info["nombre"],
            "archivo": info["archivo"],
            "listo": (CARPETA_MODELOS / info["archivo"]).exists(),
        }
        for clave, info in MODELOS.items()
    ]


# lru_cache para no cargar el .joblib en cada petición
@lru_cache(maxsize=8)
def obtener_recomendador(clave: str = "arbol") -> RecomendadorIA:
    return RecomendadorSklearn(clave or "arbol")
```

## backend/recomendador/servicio.py
```python
# Facade: une modelo, reglas y kit en una sola llamada
from catalogo.repositories import ProductoRepository

from .kits import crear_kit
from .recomendador import obtener_recomendador
from .reglas import reglas_por_defecto


# Calcula el nivel, arma el kit y regresa la respuesta completa
def recomendar(perfil: dict, modelo_id: str = "arbol", catalogo=None) -> dict:
    catalogo = catalogo or ProductoRepository()

    # Costo mínimo del kit, se le pasa a la regla de presupuesto
    def costo_minimo(nivel, datos):
        return crear_kit(nivel).costo_minimo(datos, catalogo)

    reglas = reglas_por_defecto(costo_minimo)
    resultado = obtener_recomendador(modelo_id).explicar(perfil, reglas)

    kit = crear_kit(resultado.nivel).armar(perfil, catalogo)

    respuesta = resultado.a_dict()
    respuesta["proceso"].append({
        "paso": 6,
        "titulo": "La estrategia del nivel arma el kit",
        "detalle": (
            f'crear_kit("{resultado.nivel}").armar(perfil, catalogo) elige '
            f"{len(kit['productos'])} productos con stock por ${kit['total']:,.2f}."
        ),
    })
    respuesta["kit"] = kit
    respuesta["perfil"] = {
        clave: perfil[clave] for clave in ("imc", "horas_semana", "deporte", "objetivo")
    }
    return respuesta
```

## backend/recomendador/views.py
```python
# Vistas de la API: recomendar y opciones del formulario
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .recomendador import MODELOS, modelos_disponibles
from .reglas import NIVELES
from .servicio import recomendar as recomendar_perfil
from .validacion import DEPORTES, OBJETIVOS, ErrorValidacion, validar_perfil


# Lee el JSON, revisa el modelo y valida el perfil
def leer_peticion(request):
    try:
        cuerpo = json.loads(request.body)
    except json.JSONDecodeError:
        return None, None, JsonResponse({"error": "el cuerpo debe ser JSON"}, status=400)

    modelo_id = cuerpo.pop("modelo", "arbol") or "arbol"
    if modelo_id not in MODELOS:
        return None, None, JsonResponse(
            {"error": "modelo desconocido", "modelos": list(MODELOS)}, status=400
        )
    try:
        perfil = validar_perfil(cuerpo)
    except ErrorValidacion as error:
        return None, None, JsonResponse({"error": error.mensaje, **error.detalle}, status=400)
    return perfil, modelo_id, None


# POST /recomendar/: regresa nivel, proceso y kit
@csrf_exempt
@require_POST
def recomendar(request):
    perfil, modelo_id, error = leer_peticion(request)
    if error:
        return error
    try:
        respuesta = recomendar_perfil(perfil, modelo_id)
    except FileNotFoundError as e:
        return JsonResponse({"error": str(e)}, status=503)
    return JsonResponse(respuesta, json_dumps_params={"ensure_ascii": False})


# GET /opciones/: deportes, objetivos, niveles y modelos
@require_GET
def opciones(request):
    return JsonResponse({
        "deportes": DEPORTES,
        "objetivos": OBJETIVOS,
        "niveles": NIVELES,
        "modelos": modelos_disponibles(),
    }, json_dumps_params={"ensure_ascii": False})
```

## backend/pedidos/models.py
```python
# Modelos de pedido y de sus productos
from django.db import models

from catalogo.models import NIVELES, Producto


# Pedido guardado con el perfil y el resultado de la recomendación
class Pedido(models.Model):
    folio = models.CharField(max_length=8, unique=True, db_index=True)
    creado = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default="registrado")
    cliente = models.CharField(max_length=80, blank=True)

    perfil = models.JSONField()

    modelo = models.CharField(max_length=20)
    nivel_modelo = models.CharField(max_length=20, choices=NIVELES)
    confianza_modelo = models.FloatField()
    nivel_final = models.CharField(max_length=20, choices=NIVELES)
    confianza = models.FloatField()
    corregido_por_reglas = models.BooleanField(default=False)
    motivo = models.CharField(max_length=255)
    ranking = models.JSONField(default=list)
    descartados = models.JSONField(default=list)

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dentro_de_presupuesto = models.BooleanField(default=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.folio} · {self.nivel_final}"

    # Convierte el pedido a diccionario, con o sin detalle
    def a_dict(self, detalle=True):
        datos = {
            "folio": self.folio,
            "creado": self.creado.isoformat(),
            "estado": self.estado,
            "cliente": self.cliente,
            "nivel_final": self.nivel_final,
            "confianza": self.confianza,
            "corregido_por_reglas": self.corregido_por_reglas,
            "total": float(self.total),
        }
        if detalle:
            datos.update({
                "perfil": self.perfil,
                "modelo": self.modelo,
                "nivel_modelo": self.nivel_modelo,
                "confianza_modelo": self.confianza_modelo,
                "motivo": self.motivo,
                "ranking": self.ranking,
                "descartados": self.descartados,
                "dentro_de_presupuesto": self.dentro_de_presupuesto,
                "productos": [item.a_dict() for item in self.items.all()],
            })
        return datos


# Producto incluido en un pedido con su precio al comprar
class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, related_name="items", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=120)
    tipo = models.CharField(max_length=20)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)

    # Convierte el renglón del pedido a diccionario
    def a_dict(self):
        return {
            "producto_id": self.producto_id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "precio_unitario": float(self.precio_unitario),
            "cantidad": self.cantidad,
        }
```

## backend/pedidos/repositories.py
```python
# Repositorio: guardar y consultar pedidos en la base de datos
import uuid

from django.db.models import F

from catalogo.models import Producto

from .models import Pedido, PedidoItem
from .errores import ProductoSinStock


# Patrón Repository para los pedidos
class PedidoRepository:
    # Genera un folio de 8 caracteres que no exista
    def nuevo_folio(self) -> str:
        while True:
            folio = uuid.uuid4().hex[:8].upper()
            if not Pedido.objects.filter(folio=folio).exists():
                return folio

    # Guarda el pedido y descuenta stock de cada producto
    def guardar(self, datos: dict, productos: list[dict]) -> Pedido:
        pedido = Pedido.objects.create(**datos)
        for item in productos:
            # Resta stock solo si todavía hay; si no, lanza error
            actualizados = Producto.objects.filter(
                id=item["id"], stock__gt=0
            ).update(stock=F("stock") - 1)
            if actualizados != 1:
                raise ProductoSinStock("un producto se agotó; genera una nueva recomendación")
            PedidoItem.objects.create(
                pedido=pedido,
                producto_id=item["id"],
                nombre=item["nombre"],
                tipo=item["tipo"],
                precio_unitario=item["precio"],
                cantidad=1,
            )
        return pedido

    # Busca un pedido por folio con sus productos
    def por_folio(self, folio: str):
        return (
            Pedido.objects.prefetch_related("items")
            .filter(folio=folio.strip().upper())
            .first()
        )

    # Últimos pedidos registrados
    def recientes(self, limite=50):
        return list(Pedido.objects.all()[:limite])
```

## backend/pedidos/servicios.py
```python
# Capa de servicio: lógica para registrar un pedido
from django.db import transaction

from recomendador.servicio import recomendar

from .errores import SeleccionInvalida
from .repositories import PedidoRepository


# Service Layer: recomienda el kit y guarda el pedido
def registrar_pedido(perfil: dict, modelo_id: str, cliente: str = "",
                     repositorio: PedidoRepository | None = None,
                     producto_ids: list[int] | None = None):
    repositorio = repositorio or PedidoRepository()
    resultado = recomendar(perfil, modelo_id)
    kit = resultado["kit"]

    # Si el usuario eligió productos, se validan y se recalcula el total
    if producto_ids is not None:
        disponibles = {p["id"] for p in kit["productos"]}
        if not producto_ids or len(producto_ids) != len(set(producto_ids)):
            raise SeleccionInvalida("elige al menos un producto, sin duplicados")
        if not set(producto_ids) <= disponibles:
            raise SeleccionInvalida("el kit cambió; genera una nueva recomendación")
        kit["productos"] = [
            p for p in kit["productos"] if p["id"] in producto_ids
        ]
        kit["total"] = round(sum(p["precio"] for p in kit["productos"]), 2)
        kit["dentro_de_presupuesto"] = kit["total"] <= perfil["presupuesto_mxn"]

    # Todo o nada: si falla el stock no se guarda el pedido
    with transaction.atomic():
        pedido = repositorio.guardar(
            {
                "folio": repositorio.nuevo_folio(),
                "cliente": cliente[:80],
                "perfil": perfil,
                "modelo": resultado["modelo"],
                "nivel_modelo": resultado["preferido_por_modelo"],
                "confianza_modelo": resultado["confianza_modelo"],
                "nivel_final": resultado["nivel"],
                "confianza": resultado["confianza"],
                "corregido_por_reglas": resultado["corregido_por_reglas"],
                "motivo": resultado["motivo"],
                "ranking": resultado["ranking"],
                "descartados": resultado["descartados"],
                "total": kit["total"],
                "dentro_de_presupuesto": kit["dentro_de_presupuesto"],
            },
            kit["productos"],
        )
    return pedido, resultado
```

## backend/pedidos/views.py
```python
# Vistas de la API de pedidos
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from recomendador.views import leer_peticion

from .repositories import PedidoRepository
from .errores import ProductoSinStock, SeleccionInvalida
from .servicios import registrar_pedido

repositorio = PedidoRepository()
JSON_ES = {"ensure_ascii": False}


# GET lista pedidos recientes, POST registra un pedido nuevo
@csrf_exempt
def pedidos(request):
    if request.method == "GET":
        return JsonResponse(
            {"pedidos": [p.a_dict(detalle=False) for p in repositorio.recientes()]},
            json_dumps_params=JSON_ES,
        )
    if request.method != "POST":
        return JsonResponse({"error": "método no permitido"}, status=405)

    perfil, modelo_id, error = leer_peticion(request)
    if error:
        return error
    cuerpo = json.loads(request.body)
    cliente = str(cuerpo.get("cliente", ""))
    producto_ids = cuerpo.get("producto_ids")
    # Valida que producto_ids sea una lista de enteros
    if producto_ids is not None and (
        not isinstance(producto_ids, list)
        or any(type(pid) is not int for pid in producto_ids)
    ):
        return JsonResponse({"error": "producto_ids debe ser una lista de enteros"}, status=400)
    # Los errores del servicio se convierten en códigos HTTP
    try:
        pedido, resultado = registrar_pedido(
            perfil, modelo_id, cliente, producto_ids=producto_ids
        )
    except FileNotFoundError as e:
        return JsonResponse({"error": str(e)}, status=503)
    except SeleccionInvalida as e:
        return JsonResponse({"error": str(e)}, status=409)
    except ProductoSinStock as e:
        return JsonResponse({"error": str(e)}, status=409)

    respuesta = pedido.a_dict()
    respuesta["kit"] = resultado["kit"]
    return JsonResponse(respuesta, status=201, json_dumps_params=JSON_ES)


# Devuelve un pedido por su folio o 404
def detalle_pedido(request, folio):
    pedido = repositorio.por_folio(folio)
    if pedido is None:
        return JsonResponse({"error": f"no existe el folio {folio}"}, status=404)
    return JsonResponse(pedido.a_dict(), json_dumps_params=JSON_ES)
```

## backend/asistente/adaptador.py
```python
# Adapter del clasificador de intenciones (TF-IDF + LogisticRegression)
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import joblib

RUTA_MODELO = Path(__file__).resolve().parent / "modelo" / "modelo_asistente.joblib"
# Si la confianza es menor, se toma como no entendido
UMBRAL_CONFIANZA = 0.40
INTENCION_DUDOSA = "no_entendido"


# Resultado de clasificar un mensaje
@dataclass
class Clasificacion:
    intencion: str
    confianza: float
    intencion_modelo: str
    alternativas: list = field(default_factory=list)


# Interfaz que usa el servicio, sin depender de sklearn
class AsistenteIA(ABC):
    @abstractmethod
    def clasificar(self, texto: str) -> Clasificacion:
        pass


# Adapter: carga el .joblib y lo expone como AsistenteIA
class AsistenteSklearn(AsistenteIA):
    def __init__(self, ruta: Path = RUTA_MODELO):
        if not ruta.exists():
            raise FileNotFoundError(
                f"No encuentro {ruta}. Entrena el asistente con "
                "ml/asistente/entrenar_asistente.py."
            )
        self._modelo = joblib.load(ruta)

    # Clasifica el mensaje y aplica el umbral de confianza
    def clasificar(self, texto: str) -> Clasificacion:
        probabilidades = self._modelo.predict_proba([texto])[0]
        pares = sorted(
            zip(self._modelo.classes_, probabilidades),
            key=lambda par: par[1],
            reverse=True,
        )
        mejor, confianza = pares[0]
        alternativas = [
            {"intencion": str(i), "confianza": round(float(p), 3)} for i, p in pares[:3]
        ]
        intencion = str(mejor) if confianza >= UMBRAL_CONFIANZA else INTENCION_DUDOSA
        return Clasificacion(
            intencion=intencion,
            confianza=round(float(confianza), 3),
            intencion_modelo=str(mejor),
            alternativas=alternativas,
        )


# lru_cache para cargar el modelo una sola vez
@lru_cache(maxsize=1)
def obtener_asistente() -> AsistenteIA:
    return AsistenteSklearn()
```

## backend/asistente/servicio.py
```python
# Servicio del asistente: clasifica la intención y llama su manejador
from dataclasses import asdict

from .adaptador import AsistenteIA, obtener_asistente
from .respuestas import (
    BuscarProducto,
    FueraDeDominio,
    InfoReglas,
    NoEntendido,
    PedirRecomendacion,
    PorQueNivel,
    RastreoFolio,
    Saludo,
)
from .texto import extraer_folio

# Cada intención con su manejador
MANEJADORES = {
    "saludo": Saludo,
    "rastreo_folio": RastreoFolio,
    "por_que_nivel": PorQueNivel,
    "buscar_producto": BuscarProducto,
    "pedir_recomendacion": PedirRecomendacion,
    "info_reglas": InfoReglas,
    "fuera_de_dominio": FueraDeDominio,
    "no_entendido": NoEntendido,
}


# Clasifica el mensaje, busca folio y arma la respuesta
def responder(mensaje: str, asistente: AsistenteIA | None = None) -> dict:
    asistente = asistente or obtener_asistente()
    clasificacion = asistente.clasificar(mensaje)
    folio = extraer_folio(mensaje)
    manejador = MANEJADORES.get(clasificacion.intencion, NoEntendido)()
    respuesta = manejador.responder(mensaje, folio)
    return {
        "intencion": clasificacion.intencion,
        "confianza": clasificacion.confianza,
        "intencion_modelo": clasificacion.intencion_modelo,
        "alternativas": clasificacion.alternativas,
        **asdict(respuesta),
        "folio": respuesta.folio or folio,
    }
```

## backend/asistente/views.py
```python
# Vista del chat del asistente
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .servicio import responder

LARGO_MAXIMO = 500


# POST /asistente/: valida el mensaje y regresa la respuesta
@csrf_exempt
@require_POST
def asistente(request):
    try:
        cuerpo = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "el cuerpo debe ser JSON en UTF-8"}, status=400)
    mensaje = str(cuerpo.get("mensaje") or cuerpo.get("texto") or "").strip()
    if not mensaje:
        return JsonResponse({"error": "escribe un mensaje"}, status=400)
    if len(mensaje) > LARGO_MAXIMO:
        return JsonResponse(
            {"error": f"el mensaje no debe pasar de {LARGO_MAXIMO} caracteres"}, status=400
        )
    try:
        datos = responder(mensaje)
    except FileNotFoundError as error:
        return JsonResponse({"error": str(error)}, status=503)
    return JsonResponse(datos, json_dumps_params={"ensure_ascii": False})
```

## app_flutter/lib/config/app_config.dart
```dart
// Configuración de la URL del servidor Django
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

// Guarda la URL base y avisa cambios (ChangeNotifier)
class AppConfig extends ChangeNotifier {
  static const urlPorDefecto = String.fromEnvironment(
    'API_BASE',
    defaultValue: 'http://10.0.2.2:8000',
  );
  static const _clave = 'api_base';

  String _baseUrl = urlPorDefecto;
  String get baseUrl => _baseUrl;

  // Lee la URL guardada en SharedPreferences
  Future<void> cargar() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _baseUrl = prefs.getString(_clave) ?? urlPorDefecto;
    } catch (_) {
      _baseUrl = urlPorDefecto;
    }
  }

  // Cambia la URL, avisa a los oyentes y la guarda
  Future<void> cambiarBaseUrl(String url) async {
    _baseUrl = url.trim().replaceAll(RegExp(r'/+$'), '');
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_clave, _baseUrl);
    } catch (_) {}
  }

  // Vuelve a la URL por defecto
  Future<void> restablecer() => cambiarBaseUrl(urlPorDefecto);
}
```

## app_flutter/lib/services/api_client.dart
```dart
// Cliente HTTP para hablar con el backend Django
import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';

// Error de la API con mensaje claro para mostrar
class ApiException implements Exception {
  ApiException(this.mensaje, {this.status, this.detalle});

  final String mensaje;
  final int? status;
  final Map<String, dynamic>? detalle;

  // Errores por campo que manda el backend
  Map<String, String> get errores {
    final valor = detalle?['errores'];
    if (valor is Map) {
      return valor.map((k, v) => MapEntry(k.toString(), v.toString()));
    }
    return const {};
  }

  @override
  String toString() => mensaje;
}

// Hace GET y POST y convierte la respuesta a JSON
class ApiClient {
  ApiClient(this._config, {http.Client? cliente})
    : _http = cliente ?? http.Client();

  final AppConfig _config;
  final http.Client _http;
  static const _timeout = Duration(seconds: 12);

  // Arma la URL completa con la base y los parámetros
  Uri _uri(String ruta, [Map<String, String>? query]) {
    final uri = Uri.parse('${_config.baseUrl}$ruta');
    if (query == null || query.isEmpty) return uri;
    return uri.replace(queryParameters: query);
  }

  Future<Map<String, dynamic>> get(String ruta, {Map<String, String>? query}) {
    return _enviar(() => _http.get(_uri(ruta, query)));
  }

  Future<Map<String, dynamic>> post(String ruta, Map<String, dynamic> cuerpo) {
    return _enviar(
      () => _http.post(
        _uri(ruta),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(cuerpo),
      ),
    );
  }

  // Envía la petición y traduce los errores de red y HTTP
  Future<Map<String, dynamic>> _enviar(
    Future<http.Response> Function() peticion,
  ) async {
    final http.Response respuesta;
    try {
      respuesta = await peticion().timeout(_timeout);
    } on TimeoutException {
      throw ApiException(
        'El servidor no respondió a tiempo (${_config.baseUrl}).',
      );
    } on FormatException {
      throw ApiException('La URL base no es válida: ${_config.baseUrl}');
    } on http.ClientException {
      throw ApiException(
        'No hay conexión con ${_config.baseUrl}. '
        '¿Está corriendo Django? Revisa el servidor en la pestaña Pedidos.',
      );
    } catch (e) {
      throw ApiException('Error de red: $e');
    }

    final Map<String, dynamic> datos;
    try {
      datos =
          jsonDecode(utf8.decode(respuesta.bodyBytes)) as Map<String, dynamic>;
    } catch (_) {
      throw ApiException(
        'Respuesta no válida del servidor (HTTP ${respuesta.statusCode}).',
        status: respuesta.statusCode,
      );
    }

    if (respuesta.statusCode >= 400) {
      throw ApiException(
        datos['error']?.toString() ?? 'Error HTTP ${respuesta.statusCode}',
        status: respuesta.statusCode,
        detalle: datos,
      );
    }
    return datos;
  }
}
```

## app_flutter/android/app/src/main/AndroidManifest.xml
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <application
        android:label="KitAte"
        android:usesCleartextTraffic="true"
        android:name="${applicationName}"
        android:icon="@mipmap/ic_launcher">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:taskAffinity=""
            android:theme="@style/LaunchTheme"
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|smallestScreenSize|locale|layoutDirection|fontScale|screenLayout|density|uiMode"
            android:hardwareAccelerated="true"
            android:windowSoftInputMode="adjustResize">
            <!-- Specifies an Android theme to apply to this Activity as soon as
                 the Android process has started. This theme is visible to the user
                 while the Flutter UI initializes. After that, this theme continues
                 to determine the Window background behind the Flutter UI. -->
            <meta-data
              android:name="io.flutter.embedding.android.NormalTheme"
              android:resource="@style/NormalTheme"
              />
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        <!-- Don't delete the meta-data below.
             This is used by the Flutter tool to generate GeneratedPluginRegistrant.java -->
        <meta-data
            android:name="flutterEmbedding"
            android:value="2" />
    </application>
    <!-- Required to query activities that can process text, see:
         https://developer.android.com/training/package-visibility and
         https://developer.android.com/reference/android/content/Intent#ACTION_PROCESS_TEXT.

         In particular, this is used by the Flutter engine in io.flutter.plugin.text.ProcessTextPlugin. -->
    <queries>
        <intent>
            <action android:name="android.intent.action.PROCESS_TEXT"/>
            <data android:mimeType="text/plain"/>
        </intent>
    </queries>
</manifest>
```

## .gitignore
```
# Python
.venv/
__pycache__/
*.pyc

# Material de referencia de clase (no es parte de la entrega)
_referencia_clase/
plataforma-entregas.zip

# Editor / sistema
.vscode/
.idea/
Thumbs.db
```
