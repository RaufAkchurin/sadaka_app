from sqlalchemy import desc, func, select
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.models.file import File
from app.models.fund import Fund
from app.models.payment import Payment
from app.models.project import Project
from app.models.region import Region
from app.v1.dao.base import BaseDAO


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
                func.coalesce(Fund.name, "Без фонда").label("fund_name"),
                func.coalesce(payments_subq.c.total_income, 0).label("total_income"),
                func.coalesce(payments_subq.c.unique_sponsors, 0).label("unique_sponsors"),
                func.coalesce(comments_subq.c.count_comments, 0).label("count_comments"),
                func.min(File.url).label("picture_url"),
            )
            .outerjoin(Fund, Fund.id == Project.fund_id)
            .outerjoin(File, File.project_picture_id == Project.id)
            .outerjoin(payments_subq, payments_subq.c.project_id == Project.id)
            .outerjoin(comments_subq, comments_subq.c.project_id == Project.id)
            .group_by(Project.id)
            .order_by(desc("total_income"))
        )

        result = await self._session.execute(query)
        return result.mappings().all()

    async def get_project_detail(self, data_id: int) -> tuple[Project, float, int] | None:
        # TODO ПЕРЕДЕЛАТЬ чтобы возвращало проекты а не сырые данные?
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

    async def get_projects_list(
        # TODO ПЕРЕДЕЛАТЬ чтобы возвращало проекты а не сырые данные?
        self,
        status: str | None = None,
        fund_id: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ):
        total_income = func.coalesce(func.sum(Payment.income_amount), 0).label("total_income")
        unique_sponsors = func.count(func.distinct(Payment.user_id)).label("unique_sponsors")

        base_stmt = (
            select(Project, total_income, unique_sponsors)
            .outerjoin(Payment, Payment.project_id == Project.id)
            .group_by(Project.id)
            .options(
                selectinload(Project.pictures),
                selectinload(Project.fund).selectinload(Fund.region).selectinload(Region.picture),
                selectinload(Project.stages),
            )
        )

        count_stmt = select(func.count(Project.id))

        if status is not None and status != "all":
            base_stmt = base_stmt.where(Project.status == status)
            count_stmt = count_stmt.where(Project.status == status)

        if fund_id is not None:
            base_stmt = base_stmt.where(Project.fund_id == fund_id)
            count_stmt = count_stmt.where(Project.fund_id == fund_id)

        if limit is not None:
            base_stmt = base_stmt.limit(limit)
        if offset is not None:
            base_stmt = base_stmt.offset(offset)

        rows = await self._session.execute(base_stmt)
        total_items = (await self._session.execute(count_stmt)).scalar()

        return [(proj, ti, us) for proj, ti, us in rows.all()], total_items
