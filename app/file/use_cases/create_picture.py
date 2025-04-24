from app.users.dao import FileDAO, UserDAO
from app.users.models import User
from app.users.schemas import EmailModel, UserActiveModel


class CreatePictureUseCase:
    def __init__(self, file_dao: FileDAO):
        self.users_dao = file_dao

    async def __call__(self, user: User):
        await self.users_dao.update(
            filters=EmailModel(email=user.email),
            values=UserActiveModel(
                is_active=False,
            ),
        )
