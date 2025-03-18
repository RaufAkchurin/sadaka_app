from app.dao.base import BaseDAO
from app.auth.models import User, Role


class UsersDAO(BaseDAO):
    model = User

    async def get_google_user(self, google_access_token: str):
        self.find_one_or_none()
        # query = select(self.model).filter_by(google_access_token=google_access_token)

    # async def find_one_or_none(self, filters: BaseModel):
    #     filter_dict = filters.model_dump(exclude_unset=True)
    #     logger.info(f"Поиск одной записи {self.model.__name__} по фильтрам: {filter_dict}")
    #     try:
    #         query = select(self.model).filter_by(**filter_dict)
    #         result = await self._session.execute(query)
    #         record = result.scalar_one_or_none()
    #         log_message = f"Запись {'найдена' if record else 'не найдена'} по фильтрам: {filter_dict}"
    #         logger.info(log_message)
    #         return record
    #     except SQLAlchemyError as e:
    #         logger.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
    #         raise





class RoleDAO(BaseDAO):
    model = Role
