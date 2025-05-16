from app.users.v1.dao import UserDAO
from app.users.v1.models import User
from app.users.v1.schemas import EmailModel, UserActiveModel


class DeleteUserUseCase:
    def __init__(self, users_dao: UserDAO):
        self.users_dao = users_dao

    async def __call__(self, user: User):
        await self.users_dao.update(
            filters=EmailModel(email=user.email),
            values=UserActiveModel(
                is_active=False,
            ),
        )
