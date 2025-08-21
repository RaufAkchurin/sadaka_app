from typing import List

from app.v1.users.schemas import UserInfoSchema


class GetAllUsersUseCase:
    def __init__(self, users_dao):
        self.users_dao = users_dao

    async def __call__(self) -> List[UserInfoSchema]:
        users = await self.users_dao.find_all()
        return users
