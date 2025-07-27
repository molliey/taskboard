from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.column import BoardColumn
from app.models.task import Task

