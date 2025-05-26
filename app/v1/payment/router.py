import var_dump as var_dump
from fastapi import APIRouter, Depends, Response
from models.payments import PaymentSchema
from models.user import User
from pydantic import BaseModel
from pydantic_core import Url
from sqlalchemy.ext.asyncio import AsyncSession
from v1.dependencies.auth_dep import get_current_user
from v1.dependencies.dao_dep import get_session_with_commit
from v1.payment.enums import PaymentStatusEnum
from v1.users.dao import PaymentDAO
from yookassa import Payment
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.models.currency import Currency
from yookassa.domain.models.receipt import Receipt, ReceiptItem
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder

v1_payments_router = APIRouter()


class PaymentRedirectSchema(BaseModel):
    redirect_url: Url


@v1_payments_router.post("/{project_id}/{amount}", response_model=PaymentRedirectSchema)
async def create_payment(
    project_id: int,
    amount: int,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> PaymentRedirectSchema:
    project_description = "Проект Строительство мечети"

    payment_dao = PaymentDAO(session=session)

    new_payment = await payment_dao.add(
        values=PaymentSchema(
            amount=amount,
            income_amount=amount,
            test=True,
            description=project_description,
            status=PaymentStatusEnum.PENDING,
            user_id=1,  # TODO add dynamic data
            project_id=1,  # TODO add dynamic data
            stage_id=1,  # TODO add dynamic data
        )
    )

    receipt = Receipt()
    receipt.customer = {"phone": "79990000000", "email": "test@email.com"}
    receipt.tax_system_code = 1
    receipt.items = [
        ReceiptItem(
            {
                "description": f"Пожертвование на проект {project_description}",
                "quantity": 2.0,
                "amount": {"value": amount, "currency": Currency.RUB},
                "vat_code": 2,
            }
        ),
    ]

    builder = PaymentRequestBuilder()
    builder.set_amount({"value": amount, "currency": Currency.RUB}).set_confirmation(
        {"type": ConfirmationType.REDIRECT, "return_url": "https://merchant-site.ru/return_url"}
    ).set_capture(True).set_description(f"{project_description}, айди {project_id}").set_metadata(
        {
            "new_payment": new_payment.id,
        }
    ).set_receipt(
        receipt
    )

    request = builder.build()
    res = Payment.create(request)

    var_dump.var_dump(res)

    return PaymentRedirectSchema(redirect_url=res.confirmation.confirmation_url)


@v1_payments_router.get("/yookassa_callback")
async def yookassa_callback(
    session: AsyncSession = Depends(get_session_with_commit),
):
    return Response(status_code=200)
