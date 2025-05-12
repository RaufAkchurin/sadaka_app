from typing import List

from app.payments.models import Payment
from app.project.models import Project, Stage
from app.project.schemas import ProjectPaymentsInfoSchema

# TODO add PROTOCOL
# TODO add RETURN CORRECT TYPE to __call__


class ProjectPaymentUseCaseImpl:
    def __call__(self, project: Project) -> Project:
        self.project = project
        payments = project.payments

        unique_sponsors = self.get_unique_sponsors_count(payments)
        total_collected = self.get_total_amount_collected(payments)
        collected_percentage = self.get_collected_percentage(project, total_collected)
        active_stage = self.get_active_stage()
        # stages = self.get_stages_related_info()

        payments_total = {
            "total_collected": total_collected,
            "unique_sponsors": unique_sponsors,
            "collected_percentage": collected_percentage,
        }

        project.active_stage = active_stage
        project.payments_total = ProjectPaymentsInfoSchema.model_validate(payments_total)
        return project

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

    def get_active_stage(self) -> Stage | None:
        stages = self.project.stages
        active_stage = None
        for stage in stages:
            if stage.status.value == "active":
                active_stage = stage
                break
        return active_stage

    # @staticmethod
    # def get_stages_related_info(self):
    #
    #
    #     # -необходимо
    #     # -собрали
    #     # -отчет
