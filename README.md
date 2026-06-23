<div align="center">

# DANIEL MARI · PORTAFOLIO

**Full-Stack Application · FastAPI + PostgreSQL + HTMX**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![HTMX](https://img.shields.io/badge/HTMX-1.9-3366CC?logo=htmx&logoColor=white)](https://htmx.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## TABLA DE CONTENIDO

- [Visi&oacute;n General](#visi%C3%B3n-general)
- [Arquitectura](#arquitectura)
- [Stack Tecnol&oacute;gico](#stack-tecnol%C3%B3gico)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Componentes del Sistema](#componentes-del-sistema)
  - [Capa de Presentaci&oacute;n](#capa-de-presentaci%C3%B3n)
  - [Capa de Aplicaci&oacute;n](#capa-de-aplicaci%C3%B3n)
  - [Capa de Persistencia](#capa-de-persistencia)
- [Flujo de Datos](#flujo-de-datos)
- [Esquema de Base de Datos](#esquema-de-base-de-datos)
- [API Reference](#api-reference)
- [Instalaci&oacute;n y Ejecuci&oacute;n](#instalaci%C3%B3n-y-ejecuci%C3%B3n)
- [Despliegue](#despliegue)
- [Decisiones T&eacute;cnicas](#decisiones-t%C3%A9cnicas)
- [Roadmap](#roadmap)

---

## VISIÓN GENERAL

Aplicaci&oacute;n web full-stack de una sola p&aacute;gina (SPA) que funciona como portafolio interactivo. Consume datos desde una base de datos PostgreSQL remota (Supabase) y los renderiza del lado del servidor mediante Jinja2, inyect&aacute;ndolos en el DOM v&iacute;a HTMX sin recarga de p&aacute;gina.

El frontend combina **Tailwind CSS** con t&eacute;cnicas de **glassmorphism** y **neumorphism** sobre un tema oscuro, acentuado con una tipograf&iacute;a pixel-art y animaciones CSS keyframe que le otorgan una identidad visual retro-tech distintiva.

---

## ARQUITECTURA

```
  ┌─────────────────────────────────────────────────────────────┐
  │                        CLIENTE (Browser)                    │
  │  ┌──────────┐  ┌──────────┐  ┌───────────────────────────┐ │
  │  │ Tailwind │  │  HTMX    │  │  Google Fonts             │ │
  │  │  (CDN)   │  │ (CDN)    │  │  (Press Start 2P)         │ │
  │  └──────────┘  └────┬─────┘  └───────────────────────────┘ │
  │                     │ GET /api/obtener-documentos           │
  │                     │ (hx-get)                              │
  └─────────────────────┼───────────────────────────────────────┘
                        │ HTML fragment
                        ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                   FASTAPI (ASGI Server)                     │
  │  ┌──────────────────────────────────────────────────────┐   │
  │  │  src/main.py          (Application entrypoint)       │   │
  │  │  ┌────────────────────────────────────────────────┐  │   │
  │  │  │  lifespan: conectar() / desconectar() DB pool  │  │   │
  │  │  └────────────────────────────────────────────────┘  │   │
  │  │                                                      │   │
  │  │  src/routes.py         (Controllers / Routers)       │   │
  │  │  ├── GET  / ................. index.html (landing)   │   │
  │  │  └── GET  /api/obtener-documentos  ... fragmento     │   │
  │  │                                                      │   │
  │  │  src/database.py       (Repository Pattern)          │   │
  │  │  ├── Repository_documento (Protocol / Abstracción)   │   │
  │  │  └── SupabaseAdaptador   (Implementación concreta)   │   │
  │  └──────────────────────────────────────────────────────┘   │
  └──────────────────────────┬──────────────────────────────────┘
                             │ asyncpg (SSL)
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              SUPABASE · PostgreSQL (Cloud)                  │
  │  ┌──────────────────────────────────────────────────────┐   │
  │  │  documentos                                         │   │
  │  │  ├── id                 (serial pk)                  │   │
  │  │  ├── titulo             (varchar)                    │   │
  │  │  ├── descripcion        (text)                       │   │
  │  │  ├── imagen             (text)                       │   │
  │  │  ├── content_md         (text)                       │   │
  │  │  ├── fecha_creacion     (timestamptz)                │   │
  │  │  └── url_github         (text)                       │   │
  │  └──────────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────────┘
```

### Principios Arquitect&oacute;nicos

| Principio | Aplicaci&oacute;n |
|---|---|
| **Layered Architecture** | Presentaci&oacute;n (templates) → Aplicaci&oacute;n (routes) → Persistencia (database) |
| **Repository Pattern** | `Repository_documento` protocol define el contrato; `SupabaseAdaptador` lo implementa. Permite cambiar de base de datos sin afectar routes. |
| **Dependency Injection** | FastAPI `Depends` inyecta el repositorio en los handlers de ruta. |
| **Server-Side Rendering** | Jinja2 genera HTML en el servidor; HTMX lo hidrata en el cliente sin recargar. |
| **Asynchronous I/O** | `asyncpg` + `asyncio` para operaciones de base de datos no bloqueantes. |

---

## STACK TECNOLÓGICO

### Backend

| Tecnolog&iacute;a | Versi&oacute;n | Prop&oacute;sito |
|---|---|---|
| [Python](https://python.org) | 3.13 | Lenguaje de programaci&oacute;n |
| [FastAPI](https://fastapi.tiangolo.com) | 0.136.1 | Framework web ASGI |
| [Uvicorn](https://www.uvicorn.org) | 0.49.0 | Servidor ASGI (via fastapi-cli) |
| [Jinja2](https://jinja.palletsprojects.com) | 3.1.6 | Motor de plantillas HTML |
| [asyncpg](https://magicstack.github.io/asyncpg) | 0.31.0 | Driver PostgreSQL as&iacute;ncrono |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | 1.2.2 | Carga de variables de entorno |
| [Pydantic](https://docs.pydantic.dev) | 2.13.3 | Validaci&oacute;n de datos (dependencia FastAPI) |
| [Sentry SDK](https://docs.sentry.io) | 2.63.0 | Monitoreo de errores (no inicializado) |
| [httpx](https://www.python-httpx.org) | 0.28.1 | Cliente HTTP (dependencia transitiva) |
| [python-multipart](https://github.com/andrew-d/python-multipart) | 0.0.32 | Parseo de formularios (dependencia transitiva) |

### Frontend

| Tecnolog&iacute;a | Versi&oacute;n | Carga | Prop&oacute;sito |
|---|---|---|---|
| [Tailwind CSS](https://tailwindcss.com) | 3 | CDN | Utilidades de estilo utilitarias |
| [HTMX](https://htmx.org) | 1.9.10 | CDN | Peticiones AJAX declarativas |
| [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P) | — | Google Fonts | Tipograf&iacute;a pixel-art |
| [CSS Custom](https://developer.mozilla.org/en-US/docs/Web/CSS) | — | Inline | Animaciones keyframe, glassmorphism, neumorphism |

### Herramientas

| Herramienta | Prop&oacute;sito |
|---|---|
| [uv](https://docs.astral.sh/uv) | Gestor de paquetes y entornos (alternativa a pip/poetry) |
| [Ruff](https://docs.astral.sh/ruff) | Linter y formateador de Python |
| [Heroku](https://heroku.com) | Plataforma de despliegue (ver `Procfile`) |

---

## ESTRUCTURA DEL PROYECTO

```
Portfolio/
├── .gitignore                        # Exclusiones Git (caché, .venv, builds)
├── .python-version                   # Versión de Python (3.13) para pyenv
├── Procfile                          # Comando de arranque para Heroku
├── pyproject.toml                    # Metadatos y dependencias del proyecto
├── requirements.txt                  # Dependencias pinneadas (reproducibles)
├── uv.lock                           # Lockfile de uv (instalación determinista)
├── README.md                         # Esta documentación
│
├── src/                              # CÓDIGO FUENTE
│   ├── main.py                       # Punto de entrada de la aplicación
│   ├── routes.py                     # Definición de rutas y controladores
│   └── database.py                   # Capa de abstracción de datos
│
└── static/
    └── templates/                    # Plantillas Jinja2
        ├── base.html                 # Layout base (hero, footer, estilos globales)
        ├── index.html                # Página principal (extiende base.html)
        └── documentos_fragmento.html # Fragmento HTML para inyección HTMX
```

---

## COMPONENTES DEL SISTEMA

### Capa de Presentaci&oacute;n

#### `static/templates/base.html` — Layout Base

Plantilla ra&iacute;z que define la estructura HTML global. Contiene:

- **CDN assets**: Tailwind CSS, HTMX, Google Fonts (Press Start 2P)
- **Custom CSS**: Animaci&oacute;n `slideInOut` (staggered letter reveal), clases `.glass-neumo` (glassmorphism + neumorphism combinados)
- **Hero section**: Nombre animado letra por letra con colores alternantes (rojo, verde, amarillo) y delays progresivos de 0.16s
- **Tagline**: &laquo;Seguridad, Infraestructura/Nube & Datos&raquo; con estilo monoespaciado
- **Scroll indicator**: Flecha animada con `animate-bounce` que navega a `#proyectos`
- **Bloques Jinja2**: `{% block title %}`, `{% block content %}` para extensi&oacute;n por templates hijos

#### `static/templates/index.html` — Landing Page

Extiende `base.html`. Contiene:

- **Glass-neumorphic card**: Contenedor principal con efecto de vidrio esmerilado y sombras neum&oacute;rficas
- **CTA Button**: &ldquo;CONSULTAR BASE DE DATOS&rdquo; con estilo neumorphic, animaci&oacute;n `animate-pulse`, que al hacer clic:
  1. Dispara `hx-get="/api/obtener-documentos"`
  2. Oculta el bot&oacute;n y texto instructivo (`onclick`)
  3. Inyecta el fragmento HTML en `#contenedor-cartas`
- **Contenedor de cartas**: `div#contenedor-cartas` donde se renderizan los proyectos

#### `static/templates/documentos_fragmento.html` — Fragmento de Proyectos

Renderizado por Jinja2 con la lista `documentos`. Dise&ntilde;o responsivo:

- **Layout**: Grid flexible con `sm:w-[calc(50%-12px)]`, `md:w-[calc(33.33%-16px)]`, `lg:w-64`
- **Card**: Neumorphic con sombras internas/externas, hover translateY (-1px)
- **Contenido**: T&iacute;tulo (`doc.titulo`), fecha (`doc.fecha_creacion`), descripci&oacute;n en caja con sombra inset, enlace a GitHub (`doc.url_github`)

### Capa de Aplicaci&oacute;n

#### `src/main.py` — Entrypoint

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.conectar()    # Inicializa pool asyncpg
    yield
    await db.desconectar() # Cierra pool al terminar

app = FastAPI(lifespan=lifespan)
app.include_router(landing_web)
```

- Crea instancia de FastAPI con ciclo de vida administrado
- Importa el router desde `routes.py` y el adaptador de base de datos
- El `lifespan` garantiza que la conexi&oacute;n a BD se establezca al iniciar el servidor y se cierre limpiamente al detenerlo

#### `src/routes.py` — Controladores

| Componente | Descripci&oacute;n |
|---|---|
| `router` | Instancia de `APIRouter()` de FastAPI |
| `templates` | Motor Jinja2 configurado con directorio `static/templates/` |
| `adaptador_supabase` | Instancia singleton de `SupabaseAdaptador` |
| `obtener_db()` | Funci&oacute;n de dependencia que retorna el repositorio |

**Rutas expuestas:**

| M&eacute;todo | Path | Response | Descripci&oacute;n |
|---|---|---|---|
| GET | `/` | `text/html` | P&aacute;gina principal del portafolio |
| GET | `/api/obtener-documentos` | `text/html` | Fragmento HTML con proyectos |

### Capa de Persistencia

#### `src/database.py` — Repository Pattern

Implementa el patr&oacute;n **Repository** con dos elementos:

**`Repository_documento` (Protocolo)**

```python
class Repository_documento(Protocol):
    async def obtener_todos_documentos(self) -> List[Dict[str, Any]]: ...
```

Define el contrato que cualquier repositorio de documentos debe cumplir. Al ser un `Protocol`, permite duck-typing est&aacute;tico sin herencia forzada.

**`SupabaseAdaptador` (Implementaci&oacute;n)**

| M&eacute;todo | Descripci&oacute;n |
|---|---|
| `__init__(db_url)` | Almacena URL de conexi&oacute;n, inicializa pool como `None` |
| `conectar()` | Crea contexto SSL, establece pool asyncpg (min 2, max 10 conexiones, timeout 30s) |
| `desconectar()` | Cierra el pool de conexiones |
| `obtener_todos_documentos()` | Ejecuta `SELECT ... FROM documentos ORDER BY fecha_creacion DESC`, retorna `List[Dict]` |

**Configuraci&oacute;n de conexi&oacute;n SSL:**
- `ssl.create_default_context()` como base
- `check_hostname = False` (configuraci&oacute;n para entornos controlados)
- `verify_mode = CERT_NONE` (omite validaci&oacute;n de certificado; revisar para producci&oacute;n)

---

## FLUJO DE DATOS

```
USUARIO                      SERVIDOR                     SUPABASE
   │                            │                            │
   │  GET /                     │                            │
   │───────────────────────────►│                            │
   │                            │                            │
   │  Render index.html         │                            │
   │◄───────────────────────────│                            │
   │                            │                            │
   │  Click "CONSULTAR BD"      │                            │
   │  (HTMX hx-get)             │                            │
   │───────────────────────────►│                            │
   │                            │                            │
   │                            │  SELECT * FROM            │
   │                            │  documentos                │
   │                            │  ORDER BY fecha_creacion   │
   │                            │───────────────────────────►│
   │                            │                            │
   │                            │  List[Dict] con registros  │
   │                            │◄───────────────────────────│
   │                            │                            │
   │  Render fragmento HTML     │                            │
   │  (documentos_fragmento)    │                            │
   │◄───────────────────────────│                            │
   │                            │                            │
   │  HTMX inyecta en           │                            │
   │  #contenedor-cartas        │                            │
   │  (sin recarga de página)   │                            │
```

---

## ESQUEMA DE BASE DE DATOS

```sql
CREATE TABLE documentos (
    id              SERIAL PRIMARY KEY,
    titulo          VARCHAR(255) NOT NULL,
    descripcion     TEXT,
    imagen          TEXT,             -- URL de la imagen del proyecto
    content_md      TEXT,             -- Contenido en Markdown
    fecha_creacion  TIMESTAMPTZ DEFAULT NOW(),
    url_github      TEXT              -- URL del repositorio en GitHub
);

CREATE INDEX idx_documentos_fecha ON documentos (fecha_creacion DESC);
```

### Columnas

| Columna | Tipo | Restricci&oacute;n | Descripci&oacute;n |
|---|---|---|---|
| `id` | `SERIAL` | `PRIMARY KEY` | Identificador &uacute;nico autogenerado |
| `titulo` | `VARCHAR(255)` | `NOT NULL` | Nombre del proyecto |
| `descripcion` | `TEXT` | — | Descripci&oacute;n corta del proyecto |
| `imagen` | `TEXT` | — | URL de imagen representativa |
| `content_md` | `TEXT` | — | Documentaci&oacute;n del proyecto en Markdown |
| `fecha_creacion` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Fecha de creaci&oacute;n con zona horaria |
| `url_github` | `TEXT` | — | Enlace al repositorio en GitHub |

> **Nota:** La columna `url_github` es referenciada en la plantilla `documentos_fragmento.html` (l&iacute;nea 21) pero no est&aacute; incluida en la consulta SQL de `obtener_todos_documentos()` en `database.py` (l&iacute;neas 63-66). Se debe agregar al `SELECT` o a&ntilde;adir a la tabla seg&uacute;n corresponda.

---

## API REFERENCE

### `GET /`

Retorna la p&aacute;gina principal del portafolio.

**Response** `200 OK`
```html
Content-Type: text/html

<!DOCTYPE html>
<html lang="es">
<head>...</head>
<body>
  <header id="hero">...</header>
  <main id="proyectos">...</main>
</body>
</html>
```

### `GET /api/obtener-documentos`

Ejecuta una consulta a la base de datos y retorna un fragmento HTML con las tarjetas de proyecto.

**Response** `200 OK`
```html
Content-Type: text/html

<div class="w-full sm:w-[calc(50%-12px)] ...">
  <h3>Nombre del Proyecto</h3>
  <p>2024-01-15</p>
  <p>Descripci&oacute;n del proyecto...</p>
  <a href="https://github.com/..." target="_blank">VER EN GITHUB</a>
</div>
<!-- ... m&aacute;s tarjetas ... -->
```

**Response** `500 Internal Server Error`
- Ocurre si el pool de base de datos no est&aacute; inicializado o la consulta falla
- El error se registra en consola via `print()`

---

## INSTALACIÓN Y EJECUCIÓN

### Prerrequisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/#installation) (gestor de paquetes)
- Cuenta en [Supabase](https://supabase.com) (o cualquier PostgreSQL con URL de conexi&oacute;n)

### Pasos

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd Portfolio

# 2. Crear y activar entorno virtual con uv
uv venv
source .venv/bin/activate

# 3. Sincronizar dependencias
uv sync

# 4. Configurar variables de entorno
echo "DATABASE_URL=postgresql://user:password@host:5432/postgres?sslmode=require" > .env

# 5. Ejecutar en modo desarrollo
fastapi dev src/main.py
# El servidor arrancará en http://localhost:8000
```

### Producci&oacute;n

```bash
fastapi run src/main.py --port 8000
```

### Scripts &uacute;tiles

```bash
# Lint (Ruff)
ruff check src/

# Format
ruff format src/
```

---

## DESPLIEGUE

### Heroku

El proyecto incluye un `Procfile` listo para Heroku:

```Procfile
web: fastapi run src/main.py --port $PORT
```

Pasos:

```bash
# 1. Crear app en Heroku
heroku create <app-name>

# 2. Configurar buildpack Python
heroku buildpacks:set heroku/python

# 3. Configurar variable de entorno
heroku config:set DATABASE_URL=<supabase-url>

# 4. Desplegar
git push heroku main
```

### Variables de Entorno Requeridas

| Variable | Descripci&oacute;n |
|---|---|
| `DATABASE_URL` | Cadena de conexi&oacute;n a PostgreSQL (Supabase) |
| `PORT` | Puerto del servidor (asignado por Heroku autom&aacute;ticamente) |

---

## DECISIONES TÉCNICAS

| Decisi&oacute;n | Alternativa | Justificaci&oacute;n |
|---|---|---|
| **FastAPI** vs Django/Flask | Django/Flask | Asincron&iacute;a nativa, tipado fuerte con Pydantic, documentaci&oacute;n OpenAPI autom&aacute;tica, rendimiento ASGI |
| **HTMX** vs React/Vue/Svelte | React/Vue/Svelte | Sin bundle JS, sin build step, sin virtual DOM. Hipermedia como motor de la aplicaci&oacute;n (HATEOAS). Ideal para un portafolio que prioriza SSR |
| **Tailwind CDN** vs build step | Build con PostCSS | CDN sin configuraci&oacute;n inicial; sacrifica personalizaci&oacute;n avanzada por simplicidad de despliegue |
| **asyncpg** vs psycopg2/asyncpg | psycopg2 | Driver PostgreSQL as&iacute;ncrono nativo, integraci&oacute;n directa con asyncio/FastAPI, pool de conexiones incorporado |
| **Repository Pattern** vs acceso directo | Acceso directo | Desacoplamiento: cambiar de base de datos (SQLite, MySQL, etc.) sin modificar la capa de rutas |
| **Jinja2 SSR** vs CSR | CSR (React, etc.) | SEO-friendly, First Contentful Paint m&aacute;s r&aacute;pido, menor JavaScript en cliente |
| **Glassmorphism + Neumorphism** | Planos/tradicionales | Identidad visual diferenciadora: combina est&eacute;tica moderna (glass) con profundidad f&iacute;sica (neumo) |

### Patrones de Dise&ntilde;o Implementados

| Patr&oacute;n | Ubicaci&oacute;n |
|---|---|
| **Repository** | `database.py:Repository_documento` (Protocol) + `SupabaseAdaptador` |
| **Dependency Injection** | `routes.py:obtener_db()` + FastAPI `Depends` |
| **Template Method** | `base.html` (layout) + `index.html` (extends) |
| **Singleton** | `routes.py:adaptador_supabase` (instancia &uacute;nica) |
| **Lifespan / Lifecycle** | `main.py:lifespan` (context manager de FastAPI) |

---

## ROADMAP

- [ ] Agregar `url_github` a la consulta SELECT en `database.py`
- [ ] Inicializar Sentry SDK para monitoreo de errores en producci&oacute;n
- [ ] Implementar manejo de errores con respuestas HTTP amigables
- [ ] Agregar tests automatizados (pytest + httpx)
- [ ] Migrar Tailwind CDN a build con PostCSS para personalizaci&oacute;n completa
- [ ] Mejorar configuraci&oacute;n SSL (habilitar verificaci&oacute;n de certificados)
- [ ] Sistema de cach&eacute; para respuestas de base de datos
- [ ] P&aacute;gina de detalle de proyecto con contenido Markdown renderizado

---

<div align="center">
  <br>
  <p><strong>Hecho con 🐍 Python · ⚡ FastAPI · 🎨 Tailwind CSS · 🔗 HTMX</strong></p>
  <br>
</div>
