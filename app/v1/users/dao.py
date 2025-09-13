from sqlalchemy import desc, func, select

from app.models.city import City
from app.models.comment import Comment
from app.models.country import Country
from app.models.file import File
from app.models.fund import Fund
from app.models.one_time_pass import OneTimePass
from app.models.payment import Payment
from app.models.project import Project
from app.models.referral import Referral
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

    # async def get_projects_ordered_by_payments(self):  16 запросов вместо 8, но короче
    #     query = (
    #         select(Project)
    #         .options(
    #             selectinload(Project.fund),
    #             selectinload(Project.payments),
    #             selectinload(Project.comments),
    #             selectinload(Project.pictures),
    #         )
    #     )
    #
    #     result = await self._session.execute(query)
    #     projects = result.unique().scalars().all()
    #
    #     # Доп. агрегаты считаем уже на питоне
    #     result_data = []
    #     for project in projects:
    #         total_income = sum(p.income_amount for p in project.payments)
    #         unique_sponsors = len({p.user_id for p in project.payments})
    #         count_comments = len(project.comments)
    #         first_picture = project.pictures[0].url if project.pictures else None
    #
    #         result_data.append({
    #             "id": project.id,
    #             "name": project.name,
    #             "status": project.status,
    #             "fund_name": project.fund.name if project.fund else None,
    #             "total_income": total_income,
    #             "unique_sponsors": unique_sponsors,
    #             "count_comments": count_comments,
    #             "picture_url": first_picture,
    #         })
    #
    #     # сортируем по total_income
    #     return sorted(result_data, key=lambda x: x["total_income"], reverse=True)

    async def get_projects_ordered_by_payments(self):
        # Подзапрос по платежам
        payments_subq = (
            select(
                Payment.project_id,
                func.coalesce(func.sum(Payment.income_amount), 0).label("total_income"),
                func.count(func.distinct(Payment.user_id)).label("unique_sponsors"),
            )
            .group_by(Payment.project_id)
            .subquery()
        )

        # Подзапрос по комментариям
        comments_subq = (
            select(Comment.project_id, func.count(Comment.id).label("count_comments"))
            .group_by(Comment.project_id)
            .subquery()
        )

        # Основной запрос
        query = (
            select(
                Project.id,
                Project.name,
                Project.status,
                Fund.name.label("fund_name"),
                func.coalesce(payments_subq.c.total_income, 0).label("total_income"),
                func.coalesce(payments_subq.c.unique_sponsors, 0).label("unique_sponsors"),
                func.coalesce(comments_subq.c.count_comments, 0).label("count_comments"),
                func.min(File.url).label("picture_url"),
            )
            .join(Fund, Fund.id == Project.fund_id)
            .outerjoin(File, File.project_picture_id == Project.id)
            .outerjoin(payments_subq, payments_subq.c.project_id == Project.id)
            .outerjoin(comments_subq, comments_subq.c.project_id == Project.id)
            .group_by(
                Project.id,
                Project.name,
                Project.status,
                Fund.id,
                Fund.name,
                payments_subq.c.total_income,
                payments_subq.c.unique_sponsors,
                comments_subq.c.count_comments,
            )
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


class ReferralDAO(BaseDAO):
    model = Referral
