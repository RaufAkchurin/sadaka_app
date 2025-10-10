import asyncio
import json
from ipaddress import ip_address, ip_network

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.exceptions import YookassaCallbackForbiddenException
from app.models.project import Project
from app.v1.payment_yookassa.enums import ModelPaymentStatusEnum
from app.v1.payment_yookassa.schemas import YooPaymentCreateSchema, YooWebhookDataSchema
from app.v1.project.schemas import ProjectDetailAPISchema
from app.v1.project.service import ProjectService
from app.v1.users.dao import PaymentDAO


class YooCallbackSuccessUseCaseImpl:
    # TODO add conditions for find existing payment id with status success as for TBANK callback use case
    def __init__(self, request: Request, session: AsyncSession):
        self.request = request
        self.session = session

    async def execute(self):
        await self.__yookassa_client_ip_security_checker()
        await self.__create_payment_in_db()

    async def __create_payment_in_db(self):
        self.webhook_object = await self.__get_webhook_data_object()
        webhook_object = self.webhook_object

        # TODO see problem with await self.__get_project()
        project: Project = await self.__get_project()

        payment_dao = PaymentDAO(session=self.session)
        if webhook_object.status == ModelPaymentStatusEnum.SUCCEEDED:
            await payment_dao.add(
                values=YooPaymentCreateSchema(
                    provider_payment_id=str(webhook_object.id),
                    amount=webhook_object.amount.value,
                    income_amount=webhook_object.income_amount.value,
                    test=webhook_object.test,
                    status=ModelPaymentStatusEnum.SUCCEEDED,
                    user_id=webhook_object.metadata.user_id,
                    project_id=webhook_object.metadata.project_id,
                    stage_id=project.active_stage_number,
                    created_at=webhook_object.created_at.replace(tzinfo=None),  # because yukassa give with timezone
                    # captured_at=webhook_object.captured_at.replace(tzinfo=None),  # and we save without
                )
            )
        logger.success(f"✅ Yookassa Заказ {webhook_object.id} успешно оплачен {webhook_object.amount.value}")

    async def __yookassa_client_ip_security_checker(self) -> None:
        def check_ip():
            ip_ranges = [
                "185.71.76.0/27",
                "185.71.77.0/27",
                "77.75.153.0/25",
                "77.75.156.11/32",
                "77.75.156.35/32",
                "77.75.154.128/25",
                "2a02:5180::/32",
            ]

            ip_networks = [ip_network(range) for range in ip_ranges]
            ip = ip_address(self.request.client.host)
            is_in_range = any(ip in network for network in ip_networks)
            if not is_in_range:
                raise YookassaCallbackForbiddenException

        await asyncio.to_thread(check_ip)

    async def __get_webhook_data_object(self) -> YooWebhookDataSchema:
        decoded_data = await self.request.body()
        decoded_data = decoded_data.decode("utf-8")

        object_data = json.loads(decoded_data)
        data = object_data.get("object")
        return YooWebhookDataSchema(**data)

    async def __get_project(self, project: ProjectDetailAPISchema = None) -> ProjectDetailAPISchema | None:
        service = ProjectService(session=self.session)
        project = await service.get_project_detail_by_id(project_id=self.webhook_object.metadata.project_id)
        return project
