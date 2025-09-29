from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.fund import Fund
from app.models.payment import Payment
from app.models.project import Project
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
            .having(total_income > 0)
            .options(selectinload(User.picture))
            .order_by(total_income.desc())
        )

        result = await self._session.execute(stmt)

        users = []
        for user, income in result.all():
            setattr(user, "total_income", income)
            users.append(user)

        return users

    async def get_referral_list(self, user_id: int, page: int, limit: int = 5) -> list[Referral]:
        referral_income = func.coalesce(func.sum(Payment.income_amount), 0).label("referral_income")
        referral_donors_count = func.coalesce(func.count(Payment.id), 0).label("referral_donors_count")

        stmt = (
            select(Referral, referral_income, referral_donors_count)
            .where(Referral.sharer_id == user_id)
            .outerjoin(Payment, Payment.referral_id == Referral.id)
            .outerjoin(Project, Project.id == Referral.project_id)
            .outerjoin(Fund, Fund.id == Referral.fund_id)
            .group_by(Referral.id)
            .order_by(Referral.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit + 1)
        )

        result = await self._session.execute(stmt)

        referrals = []
        for referral, income, donors_count in result.unique().all():
            setattr(referral, "referral_income", income)
            setattr(referral, "referral_donors_count", donors_count)
            referrals.append(referral)

        return referrals
