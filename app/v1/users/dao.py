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

    async def get_light_user_with_picture_by_id(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .options(
                selectinload(User.picture),  # подтянет File
                selectinload(User.city),  # подтянет City
            )
            .where(User.id == user_id)
        )

        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_user_with_referrals_by_email(self, user_email: str) -> User | None:
        stmt = (
            select(User)
            .options(
                selectinload(User.referral_gens),
                selectinload(User.referral_uses),
            )
            .where(User.email == user_email)
        )

        result = await self._session.execute(stmt)
        return result.scalars().first()


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

    async def get_regions_ordered_by_payments_for_project(self, project_id: int):
        # Сначала получим все платежи для данного проекта с информацией о регионах
        payment_subquery = (
            select(User.city_id, Payment.income_amount)
            .select_from(Payment)
            .join(User, User.id == Payment.user_id)
            .join(City, City.id == User.city_id)
            .where(Payment.project_id == project_id)
            .subquery()
        )

        total_income = func.coalesce(func.sum(payment_subquery.c.income_amount), 0.0).label("total_income")

        query = (
            select(
                Region.id,
                Region.name,
                File.url,
                total_income,
            )
            .outerjoin(City, City.region_id == Region.id)  # регион → города
            .outerjoin(payment_subquery, payment_subquery.c.city_id == City.id)  # города → платежи проекта
            .outerjoin(File, File.id == Region.picture_id)  # картинка региона
            .group_by(Region.id, Region.name, File.url)
            .order_by(desc(total_income))
        )

        result = await self._session.execute(query)
        return result.mappings().all()


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
                selectinload(Fund.projects).selectinload(Project.fund),
                selectinload(Fund.projects).selectinload(Project.payments),
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
