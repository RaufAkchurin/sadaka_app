from app.models.user import User
from app.v1.users.dao import UserDAO
from app.v1.users.schemas import UserActiveSchema, UserEmailSchema


class DeleteUserUseCase:
    def __init__(self, users_dao: UserDAO):
        self.users_dao = users_dao

    async def __call__(self, user: User):
        await self.users_dao.update(
            filters=UserEmailSchema(email=user.email),
            values=UserActiveSchema(
                is_active=False,
            ),
        )
