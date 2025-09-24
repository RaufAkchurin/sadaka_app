import datetime
import uuid

from app.models.referral import Referral, ReferralTypeEnum
from app.tests.ratings.router.schemas import TestPaymentAddSchema
from app.v1.referrals.router import ReferralAddSchema


class TestRatingAPI:
    async def test_200(self, auth_ac_super, referral_dao) -> None:
        response = await auth_ac_super.client.get("/app/v1/ratings/referrals", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 200

    async def test_prepare_data(self, auth_ac_super, referral_dao, payment_dao, session) -> None:
        now = datetime.datetime.now()

        referral_1: Referral = await referral_dao.add(ReferralAddSchema(type=ReferralTypeEnum.JOIN, sharer_id=1))

        for income_amount in [100, 200, 300]:
            uuid_num = uuid.uuid4()
            await payment_dao.add(
                TestPaymentAddSchema(
                    id=uuid_num,
                    project_id=2,
                    user_id=1,
                    income_amount=income_amount,
                    referral_id=referral_1.id,
                    stage_id=1,
                    created_at=now,
                    updated_at=now,
                    captured_at=now,
                )
            )

        referral_2: Referral = await referral_dao.add(ReferralAddSchema(type=ReferralTypeEnum.JOIN, sharer_id=2))

        for income_amount in [200, 400, 600]:
            uuid_num = uuid.uuid4()
            await payment_dao.add(
                TestPaymentAddSchema(
                    id=uuid_num,
                    project_id=2,
                    user_id=2,
                    income_amount=income_amount,
                    referral_id=referral_2.id,
                    stage_id=1,
                    created_at=now,
                    updated_at=now,
                    captured_at=now,
                )
            )

            await session.commit()

        response = await auth_ac_super.client.get("/app/v1/ratings/referrals", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 200
