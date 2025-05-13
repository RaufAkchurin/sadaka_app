from typing import List

from sqlalchemy.orm import Mapped

from app.payments.models import Payment
from app.project.models import Project, Stage
from app.project.schemas import ProjectPaymentsInfoSchema, RegionInfoSchema

# TODO add PROTOCOL
# TODO add RETURN CORRECT TYPE to __call__


class ProjectForListUseCaseImpl:
    # TODO переделать под КАРТИНКИ, а доки это для заглушки сделано
    def __call__(self, project: Project) -> Project:
        self.project = project
        payments = project.payments

        unique_sponsors = self.get_unique_sponsors_count(payments)
        total_collected = self.get_total_amount_collected(payments)
        collected_percentage = self.get_collected_percentage(project, total_collected)
        active_stage_number = self.get_active_stage_number()
        region = self.get_region()
        stages = self.get_stage_collected_field()
        pictures_list = self.get_picture_urls_field()

        payments_total = {
            "total_collected": total_collected,
            "unique_sponsors": unique_sponsors,
            "collected_percentage": collected_percentage,
        }

        project.active_stage_number = active_stage_number
        project.payments_total = ProjectPaymentsInfoSchema.model_validate(payments_total)
        project.region = region
        project.stages = stages
        project.pictures_list = pictures_list

        return project

    def get_picture_urls_field(self) -> list[str]:
        # TODO переделать под КАРТИНКИ, а доки это для заглушки сделано
        pictures = self.project.documents
        urls_list = []
        for picture in pictures:
            urls_list.append(picture.url)
        return urls_list

    @staticmethod
    def get_total_amount_collected(payments: List[Payment]) -> int:
        return sum(payment.amount for payment in payments)

    def get_collected_percentage(self, project: Project, total_collected: int) -> int:
        collected_percentage = int((total_collected / project.goal) * 100) if project.goal > 0 else 0
        return collected_percentage

    @staticmethod
    def get_unique_sponsors_count(payments: List[Payment]) -> int:
        unique_sponsors = set()
        for payment in payments:
            unique_sponsors.add(payment.user_id)
        return len(unique_sponsors)

    def get_active_stage_number(self) -> Mapped[int] | None:
        stages = self.project.stages
        active_stage = None
        for stage in stages:
            if stage.status.value == "active":
                active_stage = stage
                break
        if active_stage is None:
            return None
        return active_stage.number

    def get_region(self) -> RegionInfoSchema:
        project = self.project
        region_name = ""
        region_picture_url = ""

        if project.fund and project.fund.region and project.fund.region.picture:
            region_picture_url = project.fund.region.picture.url

        if project.fund and project.fund.region and project.fund.region.name:
            region_name = project.fund.region.name

        # Создаем объект RegionInfoSchema
        region_info = RegionInfoSchema.model_validate({"name": region_name, "picture_url": region_picture_url})

        return region_info

    def get_stage_collected_field(self) -> list[Stage]:
        stages = self.project.stages
        for stage in stages:
            collected: int = sum(payment.amount for payment in stage.payments)
            stage.collected = collected
        return stages
