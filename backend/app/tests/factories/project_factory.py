import factory
from app.models.board import Board
from faker import Faker

fake = Faker()

class BoardFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Board
        sqlalchemy_session_persistence = 'commit'

    title = factory.LazyAttribute(lambda x: fake.sentence(nb_words=3))
