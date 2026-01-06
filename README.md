# FreshKeep Backend

Plataforma de gestión inteligente de inventario de alimentos con recomendaciones de recetas basadas en IA.

## 🚀 Setup Inicial

### 1. Crear entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env y añadir tu API key de Anthropic
nano .env
```

### 4. Inicializar base de datos

La base de datos se crea automáticamente al ejecutar la app por primera vez (SQLite).

### 5. Ejecutar el servidor

```bash
# Opción 1: Usando uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Opción 2: Usando el script python
python -m app.main
```

### 6. Acceder a la documentación

Una vez el servidor esté corriendo, puedes acceder a:

- **Documentación Swagger UI**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000/

## 📁 Estructura del Proyecto

```
freshkeep-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── config.py            # Configuración (como settings.py en Django)
│   ├── database.py          # Conexión a BD
│   │
│   ├── models/              # Modelos de BD (como models.py en Django)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── recipe.py
│   │   └── notification.py
│   │
│   ├── schemas/             # Schemas Pydantic (serializers)
│   │   └── __init__.py
│   │
│   ├── api/                 # Endpoints (como views.py en Django)
│   │   └── __init__.py
│   │
│   ├── services/            # Lógica de negocio
│   │   └── __init__.py
│   │
│   └── utils/               # Utilidades
│       └── __init__.py
│
├── tests/                   # Tests
├── alembic/                 # Migraciones (como migrations en Django)
├── requirements.txt         # Dependencias
├── .env.example            # Ejemplo de variables de entorno
├── .gitignore
└── README.md
```

## 🗄️ Modelos Creados

### User (Usuario)
- email, password, nombre
- preferencias dietéticas
- tier de suscripción (free/premium)

### Product (Producto del Inventario)
- nombre, categoría
- fechas de compra y caducidad
- cantidad y unidad
- ubicación (nevera, congelador, despensa)
- estado (activo, consumido, caducado)

### Recipe (Receta)
- título, ingredientes, instrucciones
- tiempo de preparación, dificultad
- productos usados (para tracking)

### Notification (Notificación)
- tipo (caducando, caducado, sugerencia)
- mensaje, estado de lectura

## 📝 Próximos Pasos

1. ✅ Estructura base creada
2. ✅ Modelos de base de datos
3. ⏳ Crear Schemas (Pydantic)
4. ⏳ Crear endpoints de autenticación
5. ⏳ Crear endpoints de productos
6. ⏳ Integrar API de Claude para recetas
7. ⏳ Sistema de notificaciones
8. ⏳ Dashboard con estadísticas

## 🛠️ Comandos Útiles

```bash
# Ver estructura del proyecto
tree -I 'venv|__pycache__|*.pyc'

# Ejecutar tests
pytest

# Ver base de datos SQLite
sqlite3 freshkeep.db
.tables
.schema products
```

## 🔑 Variables de Entorno Necesarias

- `DATABASE_URL`: URL de conexión a la base de datos
- `SECRET_KEY`: Clave secreta para JWT
- `ANTHROPIC_API_KEY`: API key de Claude (para recetas)

## 📚 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Claude API Docs](https://docs.anthropic.com/)


# (3) Activar env en portatil
& "C:\0_Proyectos\1_nowaste\freshkeep-backend\venv\Scripts\Activate.ps1"

# (3) Activar env en torre
& "E:\0_Proyectos\1_nowaste\freshkeep-backend\venv\Scripts\Activate.ps1"
