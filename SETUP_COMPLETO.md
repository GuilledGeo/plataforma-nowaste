# ✅ FreshKeep - Entorno de Desarrollo Creado

## 🎉 ¡Listo! Has creado la estructura base del proyecto

### 📦 Archivos Creados

```
freshkeep-backend/
│
├── 📄 .env.example              ← Variables de entorno (copia a .env)
├── 📄 .gitignore                ← Archivos a ignorar en Git
├── 📄 README.md                 ← Documentación del proyecto
├── 📄 requirements.txt          ← Dependencias Python
│
└── app/
    ├── 📄 __init__.py
    ├── 📄 config.py             ← Configuración (como settings.py en Django)
    ├── 📄 database.py           ← Conexión a base de datos
    ├── 📄 main.py               ← Entry point de FastAPI ⭐
    │
    ├── models/                  ← Modelos de BD (como Django models)
    │   ├── __init__.py
    │   ├── user.py              ← Usuario ✅
    │   ├── product.py           ← Producto/Inventario ✅
    │   ├── recipe.py            ← Recetas ✅
    │   └── notification.py      ← Notificaciones ✅
    │
    ├── schemas/                 ← Schemas Pydantic (próximo paso)
    ├── api/                     ← Endpoints REST (próximo paso)
    ├── services/                ← Lógica de negocio (próximo paso)
    └── utils/                   ← Utilidades (próximo paso)
```

---

## 🚀 Cómo Ejecutar el Proyecto

### 1. Crear entorno virtual y activarlo

```bash
cd freshkeep-backend
python -m venv venv

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
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar y añadir tu API key de Anthropic
# Si no tienes API key aún, puedes dejar el resto por defecto
nano .env  # o usa tu editor favorito
```

### 4. Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

### 5. Verificar que funciona

Abre tu navegador en:
- **http://localhost:8000** ← Deberías ver un mensaje de bienvenida
- **http://localhost:8000/docs** ← Documentación automática de la API (Swagger)

---

## 📊 Modelos de Base de Datos Creados

### 1. **User** (Usuarios)
```python
- id, email, hashed_password, full_name
- dietary_preferences (preferencias alimentarias)
- subscription_tier (free/premium)
- is_active, is_superuser
- created_at, updated_at
```

### 2. **Product** (Inventario de Productos) ⭐ CORE
```python
- id, user_id, name, category
- purchase_date, expiration_date
- quantity, unit (kg, g, liters, etc)
- location (fridge, freezer, pantry)
- status (active, consumed, expired)
- image_url, notes
```

**Propiedades útiles:**
- `days_until_expiration` ← Días que faltan para caducar
- `is_expired` ← Si ya caducó
- `is_expiring_soon()` ← Si caduca pronto

### 3. **Recipe** (Recetas)
```python
- id, user_id, title
- ingredients, instructions
- prep_time, difficulty, servings
- is_ai_generated, products_used
- is_favorite
```

### 4. **Notification** (Notificaciones)
```python
- id, user_id, product_id
- type (expiring_soon, expired, recipe_suggestion)
- title, message
- is_read
```

---

## 🎯 Próximos Pasos (Desarrollo)

### Fase 1: Schemas (Serializadores) 📝
Crear los schemas de Pydantic para validar datos de entrada/salida:
- `schemas/user.py` ← UserCreate, UserResponse, UserUpdate
- `schemas/product.py` ← ProductCreate, ProductResponse, etc.
- `schemas/recipe.py`
- `schemas/notification.py`

**Similar a serializers.py en Django REST Framework**

### Fase 2: Utilidades de Seguridad 🔐
Crear funciones para autenticación:
- `utils/security.py`:
  - hash_password()
  - verify_password()
  - create_access_token()
  - get_current_user()

### Fase 3: Endpoints de Autenticación 👤
- `api/auth.py`:
  - POST /api/auth/register ← Registrar usuario
  - POST /api/auth/login ← Login (devuelve JWT)
  - GET /api/auth/me ← Info del usuario actual

### Fase 4: Endpoints de Productos 🛒
- `api/products.py`:
  - GET /api/products ← Listar productos (con filtros)
  - POST /api/products ← Crear producto
  - GET /api/products/{id} ← Ver producto
  - PUT /api/products/{id} ← Actualizar producto
  - DELETE /api/products/{id} ← Eliminar producto
  - GET /api/products/expiring-soon ← Productos por caducar ⭐

### Fase 5: Sistema de Recetas con IA 🤖
- `services/recipe_service.py`:
  - get_expiring_products() ← Obtener productos que caducan
  - generate_recipe_recommendation() ← Llamar a Claude API
  - generate_weekly_menu() ← Menú semanal
  
- `api/recipes.py`:
  - GET /api/recipes/suggest ← Sugerir recetas ⭐
  - GET /api/recipes/weekly-menu ← Menú semanal
  - POST /api/recipes ← Guardar receta favorita
  - GET /api/recipes ← Mis recetas guardadas

### Fase 6: Dashboard 📊
- `api/dashboard.py`:
  - GET /api/dashboard/stats ← Estadísticas generales
  - GET /api/dashboard/expiring ← Productos por caducar
  - GET /api/dashboard/categories ← Distribución por categorías

---

## 💡 Comparación con Django (para que te sea familiar)

| Django | FastAPI |
|--------|---------|
| `models.py` | `models/` (varios archivos) |
| `serializers.py` | `schemas/` (Pydantic) |
| `views.py` | `api/` (routers) |
| `urls.py` | Se incluyen en `main.py` |
| `settings.py` | `config.py` |
| `manage.py migrate` | `alembic upgrade head` |
| `@api_view` decorator | `@router.get()` decorator |
| Django ORM | SQLAlchemy ORM |
| `request.user` | `Depends(get_current_user)` |

---

## 🔧 Comandos Útiles

```bash
# Instalar una dependencia nueva
pip install nombre-paquete
pip freeze > requirements.txt

# Ver la base de datos (SQLite)
sqlite3 freshkeep.db
.tables
.schema products
SELECT * FROM products;

# Ejecutar con auto-reload
uvicorn app.main:app --reload

# Ver logs con más detalle
uvicorn app.main:app --reload --log-level debug
```

---

## 🎨 Enums Disponibles (Categorías predefinidas)

### ProductCategory:
- FRUITS, VEGETABLES, DAIRY, MEAT, FISH
- GRAINS, BEVERAGES, SNACKS, CONDIMENTS
- FROZEN, BAKERY, OTHER

### ProductLocation:
- FRIDGE (nevera)
- FREEZER (congelador)
- PANTRY (despensa)

### ProductStatus:
- ACTIVE (activo en inventario)
- CONSUMED (ya consumido)
- EXPIRED (caducado)
- WASTED (desperdiciado)

### NotificationType:
- EXPIRING_SOON (próximo a caducar)
- EXPIRED (ya caducado)
- LOW_STOCK (stock bajo)
- RECIPE_SUGGESTION (sugerencia de receta)

---

## 📝 Notas Importantes

1. **Base de datos**: Por defecto usa SQLite (archivo `freshkeep.db`). Fácil para desarrollo, pero cambiarás a PostgreSQL en producción.

2. **Migraciones**: Por ahora `Base.metadata.create_all()` crea las tablas automáticamente. Para producción usarás Alembic.

3. **API Key de Claude**: Necesitas una API key de Anthropic para las funciones de IA. Regístrate en https://console.anthropic.com/

4. **Documentación automática**: FastAPI genera docs automáticas en `/docs` y `/redoc`. ¡Es súper útil!

5. **Testing**: Los tests se ejecutan con `pytest`. Aún no hay tests, pero la estructura está lista.

---

## ❓ ¿Qué sigue?

Te recomiendo continuar en este orden:

1. ✅ **Probar que el servidor arranca** (`uvicorn app.main:app --reload`)
2. **Crear los Schemas de Pydantic** (validación de datos)
3. **Implementar autenticación** (register/login)
4. **Crear endpoints de productos** (CRUD básico)
5. **Integrar Claude API** para recetas
6. **Añadir sistema de notificaciones**

**¿Por dónde quieres empezar?** 🚀
