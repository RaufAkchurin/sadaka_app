from faker import Faker
from random import randint
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from app.auth.models import User, Role

faker = Faker()

# Базовая фабрика для SQLAlchemy
# Фабрика для создания ролей
class RoleFactory(SQLAlchemyFactory):
    __model__ = Role

# Функция для генерации телефона по паттерну
def generate_phone_number():
    # Генерация номера телефона в международном формате с 10-15 цифрами
    phone_number = "+7" + str(randint(100000000, 9999999999))  # Пример: +7XXXXXXXXXX
    return phone_number


# Фабрика для создания пользователей
class UserFactory(SQLAlchemyFactory):
    __model__ = User
    __set_relationships__ = True

    role = RoleFactory
    phone_number = generate_phone_number
    email = faker.email(domain='test.com')