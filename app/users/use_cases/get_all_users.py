class GetAllUsersUseCase:
    def __init__(self, users_dao):
        self.users_dao = users_dao

    async def execute(self):
        return await self.users_dao.find_all()