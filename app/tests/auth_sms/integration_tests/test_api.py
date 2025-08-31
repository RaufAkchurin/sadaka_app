from datetime import datetime, timedelta

import pytest

from app.models.user import User
from app.v1.auth_sms.schemas import OtpBlockedConfirmationsAddSchema, OtpCodeAddSchema, OtpPhoneOnlySchema

# TODO Добавить проверку на то что отправка смс была вызвана
# TODO Добавить тест эмитирующий максимально возможное количество запросов чтобы счетчики
# инкриминировались и включалась блокировка


class TestAuthSms:
    @pytest.mark.asyncio(loop_scope="session")
    @pytest.mark.parametrize(
        "phone, status_code, response_message",
        [
            ("+79990000001", 200, {"message": "Код подтверждения успешно отправлен."}),
            ("+7999", 422, None),  # невалидный телефон
            ("89991234455", 422, None),  # невалидный телефон
        ],
    )
    @pytest.mark.asyncio(loop_scope="session")
    async def test_send_code(self, ac, otp_dao, phone, status_code, response_message):
        response = await ac.post("/app/v1/auth/sms/send_code/", json={"phone": phone})
        assert response.status_code == status_code
        if response_message:
            assert response.json() == response_message

        if status_code == 200:
            otp = await otp_dao.find_one_or_none(filters=OtpPhoneOnlySchema(phone=phone))
            assert otp is not None
            assert otp.code is not None
            assert otp.expiration > datetime.now()

    @pytest.mark.usefixtures("geo_fixture")
    @pytest.mark.asyncio(loop_scope="session")
    async def test_check_code_success(self, ac, user_dao, otp_dao):
        phone = "+79990000003"
        await otp_dao.add_and_commit(
            OtpCodeAddSchema(
                phone=phone,
                code="123456",
                expiration=datetime.now() + timedelta(minutes=5),
            )
        )
        response = await ac.post(
            "/app/v1/auth/sms/check_code/",
            json={"phone": phone, "code": "123456"},
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Вы успешно авторизованы."}

        # проверяем что юзер активен
        user: User = await user_dao.find_one_or_none(filters=OtpPhoneOnlySchema(phone=phone))
        assert user is not None
        assert user.phone == phone
        assert user.is_active

    @pytest.mark.parametrize(
        "phone, " "code, status_code, detail",
        [
            ("+79990000004", "000000", 403, "Проверьте номер телефона или код подтверждения"),
        ],
    )
    @pytest.mark.asyncio(loop_scope="session")
    async def test_check_code_wrong(self, ac, otp_dao, phone, code, status_code, detail):
        await otp_dao.add_and_commit(
            OtpCodeAddSchema(
                phone=phone,
                code="123456",
                expiration=datetime.now() + timedelta(minutes=1),
            )
        )

        response = await ac.post(
            "/app/v1/auth/sms/check_code/",
            json={"phone": phone, "code": code},
        )
        assert response.status_code == status_code
        assert response.json()["detail"] == detail

    @pytest.mark.parametrize(
        "phone, " "code, status_code, detail",
        [
            ("+79990000005", "000000", 403, "Код подтверждения устарел, запросите новый"),
        ],
    )
    @pytest.mark.asyncio(loop_scope="session")
    async def test_check_code_expired(self, ac, otp_dao, phone, code, status_code, detail):
        await otp_dao.add_and_commit(
            OtpCodeAddSchema(
                phone=phone,
                code=code,
                expiration=datetime.now() - timedelta(minutes=1),
            )
        )

        response = await ac.post(
            "/app/v1/auth/sms/check_code/",
            json={"phone": phone, "code": code},
        )
        assert response.status_code == status_code
        assert response.json()["detail"] == detail

    # @pytest.mark.asyncio(loop_scope="session")
    # async def test_send_code_blocked(self, ac, otp_dao):
    #     phone = "+79990000006"
    #     # искусственно добавляем блокировку
    #     await otp_dao.add(
    #         OtpBlockedRequestAddSchema(
    #             phone=phone,
    #             code="123456",
    #             expiration=datetime.now() + timedelta(minutes=5),
    #             blocked_requests_until=datetime.now() + timedelta(hours=1),
    #         )
    #     )
    #     response = await ac.post("/app/v1/auth/sms/send_code/", json={"phone": phone})
    #     assert response.status_code == 403
    #     assert (
    #         response.json()["detail"] == "Превышен лимит на отправку смс с кодом, попробуйте попозже, или после 00-00"
    #     )

    @pytest.mark.asyncio(loop_scope="session")
    async def test_check_code_blocked(self, ac, otp_dao):
        phone = "+79990000007"
        await otp_dao.add_and_commit(
            OtpBlockedConfirmationsAddSchema(
                phone=phone,
                code="123456",
                expiration=datetime.now() + timedelta(minutes=5),
                blocked_confirmations_until=datetime.now() + timedelta(hours=1),
            )
        )
        response = await ac.post(
            "/app/v1/auth/sms/check_code/",
            json={"phone": phone, "code": "123456"},
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Превышен лимит на подтверждение кода, попробуйте попозже, или после 00-00"
