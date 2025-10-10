import json
import uuid

from fastapi import APIRouter, Depends, Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.settings import settings
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.payment_tinkoff.schemas import TBankCreatePaymentRequest
from app.v1.payment_tinkoff.use_cases.callback import TinkoffCallbackSuccessUseCaseImpl
from app.v1.payment_tinkoff.use_cases.create import TBankClient
from app.v1.utils_core.id_validators import project_id_validator

v1_tbank_router = APIRouter()


@v1_tbank_router.post("/create")
async def create_payment(
    data: TBankCreatePaymentRequest,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
):
    await project_id_validator(project_id=data.project_id, session=session)
    use_case = TBankClient(settings.T_BANK_TERMINAL_KEY, settings.T_BANK_PASSWORD)

    result = await use_case.init_payment(
        order_id=f"test_u{user_data.id}-{uuid.uuid4()}",
        amount=data.amount,
        description="Благотворительный взнос sadaka app",
        method=data.method,
        project_id=data.project_id,
        user_id=user_data.id,
    )
    # SBP → отдадим QR
    if data.method == "sbp":
        return {
            "qrUrl": result.get("Data", {}).get("Payload"),
            "paymentId": result.get("PaymentId"),
        }

    return {"paymentUrl": result["PaymentURL"], "paymentId": result["PaymentId"]}


@v1_tbank_router.post("/callback")
async def tinkoff_callback(
    request: Request,
    session: AsyncSession = Depends(get_session_with_commit),
):
    body = await request.body()
    decoded_data = body.decode("utf-8")
    object_data = json.loads(decoded_data)
    status = object_data.get("Status")
    payment_id = object_data.get("PaymentId")

    if status == "CONFIRMED":
        use_case = TinkoffCallbackSuccessUseCaseImpl(request=request, session=session)
        await use_case.execute()

    else:
        logger.success(f"Не предусмотрена обработка для Tbank callback  status: {status}, payment_id: {payment_id}")
