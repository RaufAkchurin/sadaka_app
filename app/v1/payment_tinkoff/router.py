import asyncio
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.settings import settings
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.payment_tinkoff.schemas import (
    TBankAddAccountQrRequest,
    TBankChargePaymentRequest,
    TBankChargeQrRequest,
    TBankCreatePaymentRequest,
    TBankPaymentMethodEnum,
)
from app.v1.payment_tinkoff.use_cases.callback import TinkoffCallbackSuccessUseCaseImpl
from app.v1.payment_tinkoff.use_cases.create import TBankClient
from app.v1.utils_core.id_validators import project_id_validator

v1_tbank_router = APIRouter()

@v1_tbank_router.post("/sbp/add_accountQr")
async def add_account_qr(
    data: TBankAddAccountQrRequest,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
):
    await project_id_validator(project_id=data.project_id, session=session)
    use_case = TBankClient(settings.T_BANK_TERMINAL_KEY, settings.T_BANK_PASSWORD)

    result = await use_case.add_account_qr(
        project_id=data.project_id,
        user_id=user_data.id,
        description=data.description,
    )

    return {
        "data": result.get("Data"),
        "dataType": result.get("DataType"),
        "requestKey": result.get("RequestKey"),
        "message": result.get("Message"),
        "success": result.get("Success"),
    }


@v1_tbank_router.post("/sbp/charge_qr")
async def charge_qr_payment(
    data: TBankChargeQrRequest,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
):
    await project_id_validator(project_id=data.project_id, session=session)
    use_case = TBankClient(settings.T_BANK_TERMINAL_KEY, settings.T_BANK_PASSWORD)

    init_payment = await use_case.init_payment(
        order_id=f"qr_u{user_data.id}-{uuid.uuid4()}",
        amount=data.amount,
        description="Рекуррентный донат sadaka app по СБП",
        method=TBankPaymentMethodEnum.SBP,
        project_id=data.project_id,
        user_id=user_data.id,
        recurring=True,
        data_payload={"QR": "true"},
    )

    payment_id = init_payment.get("PaymentId")

    logger.info(f"Init recurring info - {init_payment}")
    if payment_id is None:
        raise HTTPException(status_code=500, detail="Не удалось получить идентификатор платежа от T-Bank")

    result = await use_case.charge_qr(
        payment_id=payment_id,
        account_token=data.account_token)

    return {
        "success": result.get("Success"),
        "status": result.get("Status"),
        "paymentId": result.get("PaymentId"),
    }


@v1_tbank_router.post("/card/create_single")
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
        description="Донат sadaka app",
        method=TBankPaymentMethodEnum.CARD,
        project_id=data.project_id,
        user_id=user_data.id,
        customer_email=user_data.email,
        customer_phone=user_data.phone,
    )

    # logger.success(f"Init info - {result}")
    # # SBP → отдадим QR
    # if data.method == TBankPaymentMethodEnum.SBP:
    #     return {
    #         "qrUrl": result.get("QrPayload"),
    #         "paymentId": result.get("PaymentId"),
    #     }

    return {"paymentUrl": result["PaymentURL"], "paymentId": result["PaymentId"]}


@v1_tbank_router.post("/card/create_recurring")
async def create_recurring_payment(
    data: TBankCreatePaymentRequest,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
):
    await project_id_validator(project_id=data.project_id, session=session)
    use_case = TBankClient(settings.T_BANK_TERMINAL_KEY, settings.T_BANK_PASSWORD)

    result = await use_case.init_payment(
        order_id=f"recur_u{user_data.id}-{uuid.uuid4()}",
        amount=data.amount,
        description="Рекуррентный донат sadaka app",
        method=TBankPaymentMethodEnum.CARD,
        project_id=data.project_id,
        user_id=user_data.id,
        recurring=True,
        customer_email=user_data.email,
        customer_phone=user_data.phone,
    )

    logger.success(f"Init recurring info - {result}")
    return {"paymentUrl": result["PaymentURL"], "paymentId": result["PaymentId"]}


@v1_tbank_router.post("/card/charge-recurrent")
async def charge_payment(
    data: TBankChargePaymentRequest,
    user_data: User = Depends(get_current_user),
):
    use_case = TBankClient(settings.T_BANK_TERMINAL_KEY, settings.T_BANK_PASSWORD)

    new_payment =  await use_case.init_payment(
        order_id=f"test_u{user_data.id}-{uuid.uuid4()}",
        amount=data.amount,
        description="Донат sadaka app",
        method=TBankPaymentMethodEnum.CARD,
        project_id=data.project_id,
        user_id=user_data.id,
        customer_email=user_data.email,
        customer_phone=user_data.phone,
        for_rebilling=True,
    )

    result = await use_case.charge_payment(
        payment_id=new_payment.get("PaymentId"),
        rebill_id=data.rebill_id,
    )
    return {
        "success": result.get("Success"),
        "status": result.get("Status"),
        "paymentId": result.get("PaymentId"),
        "rebillId": result.get("RebillId"),
    }


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

    elif status == "ACTIVE":
        logger.success(f"Decoded data: {object_data}")

    else:
        logger.success(f"Не предусмотрена обработка для Tbank callback  status: {status}, payment_id: {payment_id}")
