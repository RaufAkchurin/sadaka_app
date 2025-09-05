from sqlalchemy import desc, func, select

from app.models.city import City
from app.models.comment import Comment
from app.models.country import Country
from app.models.file import File
from app.models.fund import Fund
from app.models.one_time_pass import OneTimePass
from app.models.payment import Payment
from app.models.project import Project
from app.models.region import Region
from app.models.stage import Stage
from app.models.user import User
from app.v1.dao.base import BaseDAO


class OneTimePassDAO(BaseDAO):
    model = OneTimePass


class CountryDAO(BaseDAO):
    model = Country


class CityDAO(BaseDAO):
    model = City


class UserDAO(BaseDAO):
    model = User

    async def get_users_ordered_by_payments(self):
        total_income = func.coalesce(
            func.sum(Payment.income_amount).over(partition_by=User.id),
            0.0,
        ).label("total_income")
        query = (
            select(User.id, User.name, File.url, total_income)
            .outerjoin(Payment, Payment.user_id == User.id)
            .outerjoin(File, File.id == User.picture_id)
            .order_by(desc("total_income"))
        )

        result = await self._session.execute(query)
        return result.unique().mappings().all()


class RegionDAO(BaseDAO):
    model = Region

    async def get_regions_ordered_by_payments(self):
        total_income = func.coalesce(
            func.sum(Payment.income_amount).over(partition_by=Region.id),
            0.0,
        ).label("total_income")

        query = (
            select(Region.id, Region.name, File.url, total_income)
            .outerjoin(City, City.region_id == Region.id)
            .outerjoin(User, User.city_id == City.id)
            .outerjoin(Payment, Payment.user_id == User.id)
            .outerjoin(File, File.id == Region.picture_id)
            .order_by(desc("total_income"))
        )

        result = await self._session.execute(query)
        return result.unique().mappings().all()


class ProjectDAO(BaseDAO):
    model = Project

    async def get_projects_ordered_by_payments(self):
        total_income = func.coalesce(func.sum(Payment.income_amount), 0.0).label("total_income")
        pictures = func.array_remove(func.array_agg(File.url), None).label("pictures")

        query = (
            select(
                Project.id,
                Project.status,
                Project.name,
                total_income,
                pictures,
            )
            .outerjoin(Payment, Payment.project_id == Project.id)
            .outerjoin(File, File.project_picture_id == Project.id)
            .group_by(Project.id, Project.status, Project.name)
            .order_by(desc("total_income"))
        )

        result = await self._session.execute(query)
        return result.mappings().all()


class FundDAO(BaseDAO):
    model = Fund


class StageDAO(BaseDAO):
    model = Stage


class FileDAO(BaseDAO):
    model = File


class PaymentDAO(BaseDAO):
    model = Payment

    async def count_payments_total_income(self) -> float:
        result = await self._session.execute(select(func.sum(self.model.income_amount)))
        return result.scalar() or 0

    async def count_payment_cities(self) -> int:
        query = (
            select(func.count(func.distinct(City.id)))
            .select_from(Payment)
            .join(User, User.id == Payment.user_id)  # тащим всех юзеров, которые есть в платежах
            .join(City, City.id == User.city_id)  # тащим города, которые есть у пользователей
        )

        result = await self._session.execute(query)
        return result.scalar() or 0


class CommentDAO(BaseDAO):
    model = Comment
