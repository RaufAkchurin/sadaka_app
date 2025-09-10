from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.v1.api_utils.pagination import Pagination, PaginationParams
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.payment_core.schemas import InstanceIdFilterSchema, MyDonationSchema
from app.v1.users.dao import PaymentDAO

v1_payments_core_router = APIRouter()


@v1_payments_core_router.get("/my_donations")
async def get_my_donations(
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
    pagination: PaginationParams = Depends(),
):
    payment_dao = PaymentDAO(session=session)
    donations = await payment_dao.find_all(filters=InstanceIdFilterSchema(user_id=user_data.id))
    serialized_donations = [MyDonationSchema.model_validate(c) for c in donations]

    return await Pagination.execute(serialized_donations, pagination.page, pagination.limit)
