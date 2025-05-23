from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from v1.dependencies.dao_dep import get_session_with_commit
from v1.payment.use_cases.create_payment import PaymentCreate, PaymentResponse
from v1.users.dao import PaymentDAO

v1_payments_router = APIRouter()


@v1_payments_router.post("/webhook/", response_model=PaymentResponse)
async def create_payment(payment: PaymentCreate, session: AsyncSession = Depends(get_session_with_commit)):
    payment_dao = PaymentDAO(session)
    payment = await payment_dao.add(payment)
    return Response(status_code=200)


# @app.get("/payments/{uuid}", response_model=PaymentResponse)
# async def read_payment(uuid: str, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Payment).filter(Payment.uuid == uuid))
#     payment = result.scalars().first()
#     if payment is None:
#         raise HTTPException(status_code=404, detail="Payment not found")
#     return payment
#
# @app.put("/payments/{uuid}", response_model=PaymentResponse)
# async def update_payment(uuid: str, payment: PaymentCreate, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Payment).filter(Payment.uuid == uuid))
#     db_payment = result.scalars().first()
#     if db_payment is None:
#         raise HTTPException(status_code=404, detail="Payment not found")
#
#     for key, value in payment.dict().items():
#         setattr(db_payment, key, value)
#
#     await db.commit()
#     await db.refresh(db_payment)
#     return db_payment
#
# @app.get("/payments/", response_model=List[PaymentResponse])
# async def read_payments(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Payment).offset(skip).limit(limit))
#     payments = result.scalars().all()
#     return payments
