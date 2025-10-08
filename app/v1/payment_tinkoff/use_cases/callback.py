import asyncio
from ipaddress import ip_address, ip_network

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.exceptions import TinkoffCallbackForbiddenException
from app.v1.payment_tinkoff.schemas import TBankCallbackSchema, TBankSuccessPaymentCreateSchema
from app.v1.project.schemas import ProjectDetailAPISchema
from app.v1.project.service import ProjectService
from app.v1.users.dao import PaymentDAO


class TinkoffCallbackSuccessUseCaseImpl:
    def __init__(self, request: Request, session: AsyncSession):
        self.request = request
        self.session = session

    async def execute(self):
        request = await self.request.json()
        request_object = request.get("object")
        if not request_object or request_object.get("Status") != "CONFIRMED":
            return

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
                "127.0.0.1",
            ]

            ip_networks = [ip_network(range) for range in ip_ranges]
            ip = ip_address(self.request.client.host)
            is_in_range = any(ip in network for network in ip_networks)
            if not is_in_range:
                print("TBANK CALLBACK SECURITY CHECKER ERROR: IP NOT IN RANGE")
                raise TinkoffCallbackForbiddenException

        await asyncio.to_thread(check_ip)

    async def __get_webhook_data_object(self) -> TBankCallbackSchema:
        body = await self.request.json()
        obj = body.get("object")
        return TBankCallbackSchema(**obj)

    async def __get_project(self):
        service = ProjectService(session=self.session)
        project = await service.get_project_detail_by_id(project_id=self.webhook_object.Data.project_id)
        if project is not None:
            return project

    async def __create_payment_in_db(self):
        self.webhook_object = await self.__get_webhook_data_object()
        webhook_object: TBankCallbackSchema = self.webhook_object

        if not webhook_object.Success or webhook_object.Status != "CONFIRMED":
            return

        project: ProjectDetailAPISchema = await self.__get_project()

        payment_dao = PaymentDAO(session=self.session)
        await payment_dao.add(
            values=TBankSuccessPaymentCreateSchema(
                provider_payment_id=str(webhook_object.PaymentId),
                amount=webhook_object.Amount,
                user_id=1,  # TODO change to DATA
                project_id=webhook_object.Data.project_id,
                stage_id=project.active_stage_number,
                # created_at=datetime.now(),
            )
        )

        print(f"✅ TБанк Заказ {webhook_object.PaymentId} успешно оплачен {webhook_object.Amount}")
