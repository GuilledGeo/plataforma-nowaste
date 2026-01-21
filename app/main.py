"""
Main - Entry Point de la aplicación FreshKeep
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Plataforma de gestión inteligente de inventario de alimentos",
    version=settings.VERSION,
    debug=settings.DEBUG,
)

# Configurar CORS - Permitir todos los orígenes en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar routers
from app.api import products, recipes, auth, analytics

app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["recipes"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])


@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "message": f"Bienvenido a {settings.APP_NAME} API",
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )