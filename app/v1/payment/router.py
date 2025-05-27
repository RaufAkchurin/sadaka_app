import json
from ipaddress import ip_address, ip_network

import var_dump as var_dump
from exceptions import YookassaCallbackForbiddenException
from fastapi import APIRouter, Depends, Response
from models.user import User
from pydantic import BaseModel
from pydantic_core import Url
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from v1.dependencies.auth_dep import get_current_user
from v1.dependencies.dao_dep import get_session_with_commit
from v1.payment.enums import PaymentStatusEnum
from v1.payment.schemas import PaymentCreateSchema, PaymentIdFilter, PaymentStatusUpdateSchema, WebhookData
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
        values=PaymentCreateSchema(
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
    (
        builder.set_amount({"value": amount, "currency": Currency.RUB})
        .set_confirmation({"type": ConfirmationType.REDIRECT, "return_url": "https://merchant-site.ru/return_url"})
        .set_capture(True)
        .set_description(f"{project_description}, айди {project_id}")
        .set_metadata(
            {
                "payment_id": new_payment.id,
                "project_id": project_id,
                "user_id": user_data.id,
            }
        )
        .set_receipt(receipt)
    )

    request = builder.build()
    res = Payment.create(request)

    var_dump.var_dump(res)

    return PaymentRedirectSchema(redirect_url=res.confirmation.confirmation_url)


async def client_ip_security(request: Request) -> None:
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
    ip = ip_address(request.client.host)
    is_in_range = any(ip in network for network in ip_networks)
    if not is_in_range:
        raise YookassaCallbackForbiddenException  # return status 200 for hiding info from criminals


async def get_webhook_data_object(request: Request) -> WebhookData:
    decoded_data = await request.body()
    decoded_data = decoded_data.decode("utf-8")

    object_data = json.loads(decoded_data)
    data = object_data.get("object")

    return WebhookData(**data)


@v1_payments_router.post("/yookassa_callback")
async def yookassa_callback(
    request: Request,
    session: AsyncSession = Depends(get_session_with_commit),
):
    # await client_ip_security(request=request)
    webhook_object = await get_webhook_data_object(request=request)

    payment_dao = PaymentDAO(session=session)
    if webhook_object.status == PaymentStatusEnum.SUCCEEDED:
        await payment_dao.update(
            filters=PaymentIdFilter(id=webhook_object.metadata.payment_id),
            values=PaymentStatusUpdateSchema(status=PaymentStatusEnum.SUCCEEDED),
        )

    else:
        await payment_dao.delete(filters=PaymentIdFilter(id=webhook_object.metadata.payment_id))

    return Response(status_code=200)
