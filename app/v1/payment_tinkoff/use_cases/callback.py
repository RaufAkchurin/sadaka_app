import asyncio
from ipaddress import ip_address, ip_network

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.exceptions import TinkoffCallbackForbiddenException
from app.models.project import Project
from app.v1.payment_tinkoff.schemas import TBankCallbackSchema, TBankPaymentCreateSchema
from app.v1.payment_yookassa.enums import PaymentStatusEnum
from app.v1.users.dao import PaymentDAO, ProjectDAO


class TinkoffCallbackSuccessUseCaseImpl:
    def __init__(self, request: Request, session: AsyncSession):
        self.request = request
        self.session = session

    async def execute(self):
        await self.__tinkoff_client_ip_security_checker()
        await self.__create_payment_in_db()

    async def __tinkoff_client_ip_security_checker(self) -> None:
        def check_ip():
            ip_ranges = [
                "91.194.226.0/23",
                "91.218.132.0/24",
                "91.218.133.0/24",
                "91.218.134.0/24",
                "91.218.135.0/24",
                "212.49.24.0/24",
                "212.233.80.0/24",
                "212.233.81.0/24",
                "212.233.82.0/24",
                "212.233.83.0/24",
                "91.194.226.181",
            ]

            ip_networks = [ip_network(range) for range in ip_ranges]
            ip = ip_address(self.request.client.host)
            is_in_range = any(ip in network for network in ip_networks)
            if not is_in_range:
                raise TinkoffCallbackForbiddenException

        await asyncio.to_thread(check_ip)

    async def __get_webhook_data_object(self) -> TBankCallbackSchema:
        body = await self.request.json()
        return TBankCallbackSchema(**body)

    async def __get_project(self) -> Project:
        project_dao = ProjectDAO(session=self.session)
        project: Project = await project_dao.find_one_or_none_by_id(data_id=self.webhook_object.data.project_id)
        return project

    async def __create_payment_in_db(self):
        self.webhook_object = await self.__get_webhook_data_object()
        webhook_object: TBankCallbackSchema = self.webhook_object

        if not webhook_object.Success or webhook_object.Status != "CONFIRMED":
            return

        project: Project = await self.__get_project()

        payment_dao = PaymentDAO(session=self.session)
        await payment_dao.add(
            values=TBankPaymentCreateSchema(
                id=webhook_object.PaymentId,
                amount=webhook_object.Amount,
                income_amount=webhook_object.income_amount.value,
                test=webhook_object.test,
                status=PaymentStatusEnum.SUCCEEDED,
                user_id=webhook_object.metadata.user_id,
                project_id=webhook_object.metadata.project_id,
                stage_id=project.active_stage_number,
                created_at=webhook_object.created_at.replace(tzinfo=None),  # because yukassa give with timezone
                captured_at=webhook_object.captured_at.replace(tzinfo=None),  # and we save without
            )
        )

        print(f"✅ TБанк Заказ {webhook_object.OrderId} успешно оплачен {webhook_object.Amount}")
