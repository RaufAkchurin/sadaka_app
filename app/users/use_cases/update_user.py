from sqlalchemy.ext.asyncio import AsyncSession
from app.geo.validators.city import city_id_validator
from app.users.dao import UsersDAO
from app.users.models import User
from app.users.schemas import UserDataUpdateSchema, EmailModel


class UpdateUserUseCase:
    def __init__(self,
                 session: AsyncSession):
        self.session = session
        self.users_dao = UsersDAO(session=session)

    async def execute(self,
                      user: User,
                      update_data: UserDataUpdateSchema) -> UserDataUpdateSchema:

        await city_id_validator(city_id=update_data.city_id, session=self.session)
        await self.users_dao.update(filters=EmailModel(email=user.email),
                                       values=UserDataUpdateSchema(
                                           name=update_data.name,
                                           city_id=update_data.city_id,
                                           email=update_data.email,
                                       )
                                    )

        updated_user = await self.users_dao.find_one_or_none_by_id(data_id=user.id)
        validated_data = UserDataUpdateSchema(
                                name=updated_user.name,
                                city_id=updated_user.city_id,
                                email=updated_user.email,
                            )
        return validated_data
