import factory
from factory.alchemy import SQLAlchemyModelFactory
from app.auth.models import User, Role
from sqlalchemy.orm import Session
from app.users.schemas import SUserAddDB
from app.tests.conftest import session


class BaseFactory(SQLAlchemyModelFactory):
    # Базовый класс для всех фабрик, которые работают с SQLAlchemy.
    # Прокидываем сессию в Meta и создаем общую логику для всех фабрик.
    class Meta:
        sqlalchemy_session_persistence = "commit"  # Настройка для сохранения объектов в БД

    @classmethod
    def set_session(cls, session: Session):
        # Устанавливаем сессию для всех фабрик.
        cls.Meta.sqlalchemy_session = session

class RoleFactory(BaseFactory):
    class Meta:
        model = Role
    id = factory.LazyFunction(int)
    name = factory.Faker("word")


class UserFactory(BaseFactory):
    class Meta:
        model = User

    id = factory.LazyFunction(int)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    password = factory.Faker("password")
    role = factory.SubFactory(RoleFactory)  # Ссылка на RoleFactory для создания роли


async def test_add_and_get_new_user(user_dao):
    user_factory = UserFactory.build()
    user_data = {
        "first_name": user_factory.first_name,
        "last_name": user_factory.last_name,
        "email": user_factory.email,
        "password": user_factory.password,
        }

    # Добавление пользователя
    new_user = await user_dao.add(values=SUserAddDB(**user_data))
    assert new_user.id == 7
    assert new_user is not None
