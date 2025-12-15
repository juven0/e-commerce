
"""
Repository pour User
Gestion de l'accès aux données utilisateurs
"""

from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.user import User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository pour gérer les utilisateurs"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email
        
        Args:
            email: Email de l'utilisateur
        
        Returns:
            Utilisateur ou None
        """
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_email_verified(self, email: str) -> Optional[User]:
        """
        Récupère un utilisateur vérifié par son email
        
        Args:
            email: Email de l'utilisateur
        
        Returns:
            Utilisateur vérifié ou None
        """
        query = select(User).where(
            User.email == email,
            User.email_verified_at.is_not(None)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un email existe déjà
        
        Args:
            email: Email à vérifier
            exclude_id: ID à exclure de la vérification
        
        Returns:
            True si existe, False sinon
        """
        query = select(User.id).where(User.email == email)
        
        if exclude_id:
            query = query.where(User.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def verify_email(self, user_id: int) -> Optional[User]:
        """
        Marque l'email d'un utilisateur comme vérifié
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Utilisateur mis à jour
        """
        return await self.update(user_id, {
            "email_verified_at": datetime.utcnow()
        })
    
    async def update_password(self, user_id: int, password_hash: str) -> Optional[User]:
        """
        Met à jour le mot de passe d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            password_hash: Hash du nouveau mot de passe
        
        Returns:
            Utilisateur mis à jour
        """
        return await self.update(user_id, {"password_hash": password_hash})
    
    async def activate(self, user_id: int) -> Optional[User]:
        """
        Active un compte utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Utilisateur activé
        """
        return await self.update(user_id, {"is_active": True})
    
    async def deactivate(self, user_id: int) -> Optional[User]:
        """
        Désactive un compte utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Utilisateur désactivé
        """
        return await self.update(user_id, {"is_active": False})
    
    async def update_role(self, user_id: int, role: UserRole) -> Optional[User]:
        """
        Met à jour le rôle d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            role: Nouveau rôle
        
        Returns:
            Utilisateur mis à jour
        """
        return await self.update(user_id, {"role": role})
    
    async def get_all_active(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Récupère tous les utilisateurs actifs
        
        Args:
            skip: Offset
            limit: Limite
        
        Returns:
            Liste d'utilisateurs actifs
        """
        query = (
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Récupère les utilisateurs par rôle
        
        Args:
            role: Rôle recherché
            skip: Offset
            limit: Limite
        
        Returns:
            Liste d'utilisateurs
        """
        query = (
            select(User)
            .where(User.role == role)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def search(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Recherche d'utilisateurs par nom ou email
        
        Args:
            search_term: Terme de recherche
            skip: Offset
            limit: Limite
        
        Returns:
            Liste d'utilisateurs correspondants
        """
        search_pattern = f"%{search_term}%"
        query = (
            select(User)
            .where(
                or_(
                    User.email.ilike(search_pattern),
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern)
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_by_role(self, role: UserRole) -> int:
        """
        Compte les utilisateurs par rôle
        
        Args:
            role: Rôle à compter
        
        Returns:
            Nombre d'utilisateurs
        """
        return await self.count(role=role)
    
    async def count_active(self) -> int:
        """
        Compte les utilisateurs actifs
        
        Returns:
            Nombre d'utilisateurs actifs
        """
        return await self.count(is_active=True)