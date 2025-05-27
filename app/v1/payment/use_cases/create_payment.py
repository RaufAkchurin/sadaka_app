import var_dump as var_dump
from models.project import Project
from models.user import User
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from v1.payment.enums import PaymentStatusEnum
from v1.payment.schemas import PaymentCreateSchema, PaymentUrlSchema
from v1.users.dao import PaymentDAO
from yookassa import Payment
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.models.currency import Currency
from yookassa.domain.models.receipt import Receipt, ReceiptItem
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder


class CreatePaymentUseCaseImpl(BaseModel):
    session: AsyncSession
    amount: int
    user_data: User
    project_id: int
    return_url: str

    async def execute(self):
        built_payment = await self.yoo_payment_build()
        return PaymentUrlSchema(redirect_url=built_payment.confirmation.confirmation_url)

    @property
    async def project(self) -> Project:
        payment_dao = PaymentDAO(session=self.session)
        project = await payment_dao.find_one_or_none_by_id(data_id=self.project_id)
        return project

    @property
    async def create_payment_in_db(self) -> Payment:
        payment_dao = PaymentDAO(session=self.session)

        new_payment = await payment_dao.add(
            values=PaymentCreateSchema(
                amount=self.amount,
                income_amount=self.amount,
                test=True,
                status=PaymentStatusEnum.PENDING,
                user_id=self.user_id,
                project_id=self.project_id,
                stage_id=1,  # TODO add dynamic data
            )
        )
        return new_payment

    async def yoo_payment_build(self) -> Payment:
        project = await self.project

        receipt = Receipt()
        receipt.customer = {"email": self.user_data.email}
        receipt.tax_system_code = 1
        receipt.items = [
            ReceiptItem(
                {
                    "description": f"Пожертвование на проект {project.description}",
                    "quantity": 2.0,
                    "amount": {"value": self.amount, "currency": Currency.RUB},
                    "vat_code": 2,
                }
            ),
        ]

        builder = PaymentRequestBuilder()
        (
            builder.set_amount({"value": self.amount, "currency": Currency.RUB})
            .set_confirmation({"type": ConfirmationType.REDIRECT, "return_url": self.return_url})
            .set_capture(True)
            .set_description(f"{self.project_description}, айди {self.project_id}")
            .set_metadata(
                {
                    "payment_id": await self.create_payment_in_db.id,
                    "project_id": self.project_id,
                    "user_id": self.user_id,
                }
            )
            .set_receipt(receipt)
        )

        request = builder.build()
        built_payment = Payment.create(request)

        var_dump.var_dump(built_payment)  # вывод всей структуры в логи
        return built_payment
