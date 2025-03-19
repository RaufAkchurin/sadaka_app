from faker import Faker
from random import randint
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from app.auth.models import User, Role

faker = Faker()

# Базовая фабрика для SQLAlchemy
# Фабрика для создания ролей
class RoleFactory(SQLAlchemyFactory):
    __model__ = Role

# Фабрика для создания пользователей
class UserFactory(SQLAlchemyFactory):
    __model__ = User
    __set_relationships__ = True

    role = RoleFactory
    email = faker.email(domain='test.com')