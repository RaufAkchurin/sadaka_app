import uuid
from datetime import datetime
from typing import Dict, Optional

from app.v1.payment_t_bank.schemas import PaymentResponse, PaymentStatus


class PaymentStorage:
    def __init__(self):
        self._payments: Dict[str, PaymentResponse] = {}

    def create_payment(self, amount: float, order_id: str, user_id: str) -> PaymentResponse:
        payment_id = str(uuid.uuid4())
        payment = PaymentResponse(
            payment_id=payment_id,
            status=PaymentStatus.PENDING,
            amount=amount,
            order_id=order_id,
            created_at=datetime.now(),
        )
        self._payments[payment_id] = payment
        return payment

    def get_payment(self, payment_id: str) -> Optional[PaymentResponse]:
        return self._payments.get(payment_id)

    def update_payment_status(self, payment_id: str, status: PaymentStatus, payment_url: str = None) -> bool:
        if payment_id in self._payments:
            self._payments[payment_id].status = status
            if payment_url:
                self._payments[payment_id].payment_url = payment_url
            return True
        return False


payment_storage = PaymentStorage()
