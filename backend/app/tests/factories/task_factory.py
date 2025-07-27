import factory
from app.models.task import Task, TaskStatus
from faker import Faker
from datetime import datetime

fake = Faker()

class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Task
        sqlalchemy_session_persistence = 'commit'

    title = factory.LazyAttribute(lambda x: fake.sentence(nb_words=5))
    description = factory.LazyAttribute(lambda x: fake.text(max_nb_chars=100))
    status = TaskStatus.TODO
    project = factory.LazyAttribute(lambda x: fake.word())
    created_at = factory.LazyAttribute(lambda x: datetime.utcnow())
    updated_at = None
    done = False
