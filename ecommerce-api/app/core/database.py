
"""
Configuration de la base de données
SQLAlchemy 2.0 avec support async (asyncmy pour MySQL)
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase, declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import MetaData

from app.core.config import settings


# ===== Conventions de nommage pour les contraintes =====
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)


# ===== Classe de base pour tous les modèles =====
class Base(DeclarativeBase):
    """
    Classe de base pour tous les modèles SQLAlchemy
    Utilise la nouvelle syntaxe SQLAlchemy 2.0
    """
    metadata = metadata
    
    # Permet de définir __tablename__ automatiquement
    # basé sur le nom de la classe
    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


# ===== Configuration du moteur de base de données =====
def create_engine() -> AsyncEngine:
    """
    Crée et configure le moteur de base de données async
    """
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,  # Log les requêtes SQL en dev
        pool_pre_ping=True,  # Vérifie la connexion avant utilisation
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_recycle=3600,  # Recycle les connexions après 1h
        pool_use_lifo=True,  # LIFO pour réutiliser les connexions chaudes
    )
    return engine


# Instance globale du moteur
engine: AsyncEngine = create_engine()


# ===== Session Factory =====
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Permet d'accéder aux objets après commit
    autocommit=False,
    autoflush=False,
)


# ===== Dependency pour FastAPI =====
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Générateur de session de base de données pour FastAPI
    Usage: db: AsyncSession = Depends(get_db)
    
    Gère automatiquement:
    - L'ouverture de la session
    - Le commit en cas de succès
    - Le rollback en cas d'erreur
    - La fermeture de la session
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ===== Fonctions utilitaires =====
async def init_db() -> None:
    """
    Initialise la base de données
    Crée toutes les tables si elles n'existent pas
    
    NOTE: En production, utiliser Alembic pour les migrations
    """
    async with engine.begin() as conn:
        # Importer tous les modèles ici pour que SQLAlchemy les connaisse
        from app.models import (
            user, address, category, product, 
            cart, order, payment, review, coupon, activity_log
        )
        
        # Crée toutes les tables
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """
    Supprime toutes les tables de la base de données
    ATTENTION: À utiliser uniquement en développement !
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db() -> None:
    """
    Ferme toutes les connexions à la base de données
    À appeler lors de l'arrêt de l'application
    """
    await engine.dispose()


# ===== Context Manager pour transactions manuelles =====
class DatabaseTransaction:
    """
    Context manager pour gérer manuellement les transactions
    
    Usage:
        async with DatabaseTransaction() as session:
            # Faire des opérations
            await session.execute(...)
    """
    
    def __init__(self):
        self.session: AsyncSession | None = None
    
    async def __aenter__(self) -> AsyncSession:
        self.session = async_session_maker()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()


# ===== Helper pour testing =====
async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Session de base de données pour les tests
    Utilise une base de données de test séparée
    """
    if not settings.TEST_DATABASE_URL:
        raise ValueError("TEST_DATABASE_URL n'est pas défini")
    
    test_engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool  # Pas de pool pour les tests
    )
    
    test_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with test_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    await test_engine.dispose()