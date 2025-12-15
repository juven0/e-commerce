
"""
Repository de base générique
Pattern Repository pour abstraire l'accès aux données
"""

from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Repository de base générique avec opérations CRUD
    Toutes les méthodes sont asynchrones
    """
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialise le repository
        
        Args:
            model: Classe du modèle SQLAlchemy
            db: Session de base de données async
        """
        self.model = model
        self.db = db
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Récupère un enregistrement par son ID
        
        Args:
            id: Identifiant de l'enregistrement
        
        Returns:
            Enregistrement ou None
        """
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Récupère tous les enregistrements avec pagination
        
        Args:
            skip: Nombre d'enregistrements à sauter
            limit: Nombre maximum d'enregistrements
            order_by: Colonne pour le tri
        
        Returns:
            Liste d'enregistrements
        """
        query = select(self.model).offset(skip).limit(limit)
        
        if order_by:
            if hasattr(self.model, order_by):
                query = query.order_by(getattr(self.model, order_by))
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def create(self, obj_in: dict) -> ModelType:
        """
        Crée un nouvel enregistrement
        
        Args:
            obj_in: Données à insérer (dict)
        
        Returns:
            Enregistrement créé
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        """
        Met à jour un enregistrement
        
        Args:
            id: Identifiant de l'enregistrement
            obj_in: Données à mettre à jour
        
        Returns:
            Enregistrement mis à jour ou None
        """
        # Filtrer les valeurs None
        update_data = {k: v for k, v in obj_in.items() if v is not None}
        
        if not update_data:
            return await self.get_by_id(id)
        
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        
        await self.db.execute(query)
        await self.db.flush()
        
        return await self.get_by_id(id)
    
    async def delete(self, id: int) -> bool:
        """
        Supprime un enregistrement
        
        Args:
            id: Identifiant de l'enregistrement
        
        Returns:
            True si supprimé, False sinon
        """
        query = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        await self.db.flush()
        
        return result.rowcount > 0
    
    async def count(self, **filters) -> int:
        """
        Compte le nombre d'enregistrements
        
        Args:
            **filters: Filtres optionnels
        
        Returns:
            Nombre d'enregistrements
        """
        query = select(func.count(self.model.id))
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def exists(self, id: int) -> bool:
        """
        Vérifie si un enregistrement existe
        
        Args:
            id: Identifiant de l'enregistrement
        
        Returns:
            True si existe, False sinon
        """
        query = select(func.count(self.model.id)).where(self.model.id == id)
        result = await self.db.execute(query)
        count = result.scalar_one()
        return count > 0
    
    async def get_multi_by_ids(self, ids: List[int]) -> List[ModelType]:
        """
        Récupère plusieurs enregistrements par leurs IDs
        
        Args:
            ids: Liste d'identifiants
        
        Returns:
            Liste d'enregistrements
        """
        query = select(self.model).where(self.model.id.in_(ids))
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def bulk_create(self, objects: List[dict]) -> List[ModelType]:
        """
        Crée plusieurs enregistrements en une seule opération
        
        Args:
            objects: Liste de dictionnaires de données
        
        Returns:
            Liste d'enregistrements créés
        """
        db_objects = [self.model(**obj) for obj in objects]
        self.db.add_all(db_objects)
        await self.db.flush()
        
        for obj in db_objects:
            await self.db.refresh(obj)
        
        return db_objects
    
    async def bulk_update(self, updates: List[dict]) -> bool:
        """
        Met à jour plusieurs enregistrements
        
        Args:
            updates: Liste de dicts avec 'id' et les champs à mettre à jour
        
        Returns:
            True si succès
        """
        for update_data in updates:
            if 'id' not in update_data:
                continue
            
            obj_id = update_data.pop('id')
            await self.update(obj_id, update_data)
        
        return True
    
    async def bulk_delete(self, ids: List[int]) -> int:
        """
        Supprime plusieurs enregistrements
        
        Args:
            ids: Liste d'identifiants
        
        Returns:
            Nombre d'enregistrements supprimés
        """
        query = delete(self.model).where(self.model.id.in_(ids))
        result = await self.db.execute(query)
        await self.db.flush()
        
        return result.rowcount