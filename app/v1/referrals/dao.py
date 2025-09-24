from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.payment import Payment
from app.models.referral import Referral
from app.models.user import User
from app.v1.dao.base import BaseDAO


class ReferralDAO(BaseDAO):
    model = Referral

    async def get_users_sorted_by_ref_income(self):
        total_income = func.coalesce(func.sum(Payment.income_amount), 0).label("total_income")

        stmt = (
            select(User, total_income)
            .outerjoin(Referral, Referral.sharer_id == User.id)
            .outerjoin(Payment, Payment.referral_id == Referral.id)
            .group_by(User.id)
            .options(selectinload(User.picture))
            .order_by(total_income.desc())
        )

        result = await self._session.execute(stmt)

        users = []
        for user, income in result.all():
            setattr(user, "total_income", income)
            users.append(user)

        return users
