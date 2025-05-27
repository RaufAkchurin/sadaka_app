import json
from ipaddress import ip_address, ip_network

from exceptions import YookassaCallbackForbiddenException
from fastapi import APIRouter, Depends, Response
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from v1.dependencies.auth_dep import get_current_user
from v1.dependencies.dao_dep import get_session_with_commit
from v1.payment.enums import PaymentStatusEnum
from v1.payment.schemas import PaymentIdFilter, PaymentStatusUpdateSchema, PaymentUrlSchema, WebhookData
from v1.payment.use_cases.create_payment import CreatePaymentUseCaseImpl
from v1.users.dao import PaymentDAO

v1_payments_router = APIRouter()


@v1_payments_router.post("/{project_id}/{amount}", response_model=PaymentUrlSchema)
async def create_payment(
    project_id: int,
    amount: int,
    return_url: str,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> PaymentUrlSchema:
    use_case = CreatePaymentUseCaseImpl(
        session=session, project_id=project_id, amount=amount, user_data=user_data, return_url=return_url
    )
    redirect_url = await use_case.execute()

    return redirect_url


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
) -> Response:
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
