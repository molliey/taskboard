from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.auth import get_password_hash
from typing import Optional, List

class UserService:
    """Service class for user-related business logic."""
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            db: Database session
            user: User creation data
            
        Returns:
            Created user object
        """
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User object or None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            db: Database session
            username: Username
            
        Returns:
            User object or None
        """
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            db: Database session
            email: Email address
            
        Returns:
            User object or None
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get a list of users with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of users
        """
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def search_users(db: Session, query: str, limit: int = 10) -> List[User]:
        """
        Search users by username, email, or full name.
        
        Args:
            db: Database session
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching users
        """
        search = f"%{query}%"
        return db.query(User).filter(
            or_(
                User.username.ilike(search),
                User.email.ilike(search),
                User.full_name.ilike(search)
            )
        ).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """
        Update user information.
        
        Args:
            db: Database session
            user_id: User ID
            user_update: Update data
            
        Returns:
            Updated user object or None
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        
        # Handle password update separately
        if "password" in update_data:
            hashed_password = get_password_hash(update_data.pop("password"))
            db_user.hashed_password = hashed_password
        
        # Update other fields
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> Optional[User]:
        """
        Deactivate a user account.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Deactivated user object or None
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db_user.is_active = False
            db.commit()
            db.refresh(db_user)
        return db_user