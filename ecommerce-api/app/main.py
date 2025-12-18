
"""
Point d'entrée de l'application FastAPI E-commerce
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1 import api_router


# ===== Lifespan Events =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application
    """
    # Startup
    print("🚀 Démarrage de l'application...")
    print(f"📦 {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"🌍 Environnement: {settings.ENVIRONMENT}")
    
    # Initialiser la base de données (optionnel, préférer Alembic)
    if settings.DEBUG:
        print("🔧 Mode DEBUG activé")
    
    yield
    
    # Shutdown
    print("🛑 Arrêt de l'application...")
    await close_db()
    print("✅ Connexions fermées")


# ===== Application FastAPI =====
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API E-commerce complète avec FastAPI",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)


# ===== Middlewares =====

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=["*"],
)

# Trusted Host (sécurité)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # À configurer selon vos domaines
    )


# Middleware de timing des requêtes
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Ajoute le temps de traitement dans les headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ===== Exception Handlers =====

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handler personnalisé pour 404"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Ressource non trouvée"}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handler personnalisé pour 500"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erreur interne du serveur"}
    )


# ===== Routes =====

@app.get(
    "/",
    tags=["Root"],
    summary="Page d'accueil de l'API"
)
async def root():
    """Route racine de l'API"""
    return {
        "message": f"Bienvenue sur {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else "Documentation désactivée en production",
        "status": "operational"
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check"
)
async def health_check():
    """Vérifie l'état de l'API"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Inclure le router API v1
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX
)


# ===== Point d'entrée =====
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )