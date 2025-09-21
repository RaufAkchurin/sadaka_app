from sqlalchemy import desc, func, select
from sqlalchemy.orm import selectinload

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
from app.v1.fund.schemas import FundDetailAPISchema
from app.v1.project.schemas import FileBaseSchema, ProjectForListAPISchema


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

    async def get_light_user_by_id(self, user_id: int) -> User | None:
        stmt = select(
            User.id,
            User.role,
            User.is_active,
            User.email,
            User.name,
            User.is_anonymous,
            User.language,
        ).where(User.id == user_id)
        result = await self._session.execute(stmt)
        return result.first()


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

    async def get_fund_detail(self, data_id: int) -> tuple[Project, float, int] | None:
        total_income = func.coalesce(func.sum(Payment.income_amount), 0).label("total_income")
        unique_sponsors = func.count(func.distinct(Payment.user_id)).label("unique_sponsors")

        stmt = (
            select(Project, total_income, unique_sponsors)
            .outerjoin(Payment, Payment.project_id == Project.id)
            .where(Project.id == data_id)
            .group_by(Project.id)
            .options(
                selectinload(Project.documents),
                selectinload(Project.pictures),
                selectinload(Project.stages),
                selectinload(Project.comments),
                selectinload(Project.referrals),
                selectinload(Project.fund).selectinload(Fund.region).selectinload(Region.picture),
            )
        )

        result = await self._session.execute(stmt)
        row = result.first()
        if row is None:
            return None

        project, total_income, unique_sponsors = row
        return project, total_income, unique_sponsors


class FundDAO(BaseDAO):
    model = Fund

    async def get_fund_detail(self, fund_id: int):
        # агрегаты по платежам для фонда
        payments_subq = (
            select(
                Project.fund_id.label("fund_id"),
                func.coalesce(func.sum(Payment.income_amount), 0).label("total_income"),
                func.count(Project.id.distinct()).label("projects_count"),
            )
            .join(Project, Project.id == Payment.project_id, isouter=True)
            .group_by(Project.fund_id)
            .subquery()
        )

        query = (
            select(Fund)
            .options(
                # тянем регион
                selectinload(Fund.region),
                # тянем документы
                selectinload(Fund.documents),
                # тянем проекты + их вложенные данные
                selectinload(Fund.projects).selectinload(Project.pictures),
                selectinload(Fund.projects).selectinload(Project.stages),
            )
            .join(payments_subq, payments_subq.c.fund_id == Fund.id, isouter=True)
            .where(Fund.id == fund_id)
        )

        result = await self._session.execute(query)
        fund: Fund = result.unique().scalar_one_or_none()
        if not fund:
            return None

        # мапим в схему
        return FundDetailAPISchema(
            id=fund.id,
            name=fund.name,
            description=fund.description,
            hot_line=fund.hot_line,
            address=fund.address,
            region_name=fund.region.name if fund.region else None,
            documents=[FileBaseSchema.model_validate(doc) for doc in fund.documents],
            projects=[ProjectForListAPISchema.model_validate(prj) for prj in fund.projects],
            total_income=getattr(fund, "total_income", 0.0),
            projects_count=getattr(fund, "projects_count", 0),
        )


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
