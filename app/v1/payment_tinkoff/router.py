from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import settings
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.payment_tinkoff.schemas import TBankCreatePaymentRequest
from app.v1.payment_tinkoff.use_cases.callback import TinkoffCallbackSuccessUseCaseImpl
from app.v1.payment_tinkoff.use_cases.create import TBankPaymentCreateUseCaseImpl

v1_tinkoff_router = APIRouter()


@v1_tinkoff_router.post("/create")
async def create_payment(data: TBankCreatePaymentRequest):
    use_case = TBankPaymentCreateUseCaseImpl(settings.T_BANK_TERMINAL_KEY, settings.T_BANK_PASSWORD)
    result = await use_case.init_payment(
        order_id=data.order_id,
        amount=data.amount,
        description=data.description,
        method=data.method,
        project_id=data.project_id,
    )
    # SBP → отдадим QR
    if data.method == "sbp":
        return {
            "qrUrl": result.get("Data", {}).get("Payload"),
            "paymentId": result.get("PaymentId"),
        }

    return {"paymentUrl": result["PaymentURL"], "paymentId": result["PaymentId"]}


@v1_tinkoff_router.post("/callback")
async def tinkoff_callback(request: Request, session: AsyncSession = Depends(get_session_with_commit)):
    use_case = TinkoffCallbackSuccessUseCaseImpl(request=request, session=session)
    await use_case.execute()
