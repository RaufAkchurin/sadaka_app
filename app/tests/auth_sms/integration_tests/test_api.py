from datetime import datetime, timedelta

import pytest

from app.v1.auth_sms.schemas import OtpPhoneOnlySchema, OtpAddSchema


class TestAuthSms:
    @pytest.mark.parametrize(
        "phone, status_code, response_message",
        [
            ("+79990000001", 200, {"message": "Код подтверждения успешно отправлен."}),
            ("+7999", 422, None),  # невалидный телефон
        ],
    )
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

    async def test_send_code_blocked(self, ac, otp_dao):
        phone = "+79990000002"
        # искусственно добавляем блокировку
        await otp_dao.add(
            OtpAddSchema(
                phone=phone,
                code="123456",
                expiration=datetime.now() + timedelta(minutes=5),
                blocked_requests_until=datetime.now() + timedelta(hours=1),
            )
        )
        response = await ac.post("/app/v1/auth/sms/send_code/", json={"phone": phone})
        assert response.status_code == 403
        assert response.json()["detail"] == "Превышено число запросов кода"

    async def test_check_code_success(self, ac, user_dao, otp_dao):
        phone = "+79990000003"
        await otp_dao.add(
            OtpAddSchema(
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
        user = await user_dao.find_one_or_none(filters=OtpPhoneOnlySchema(phone=phone))
        assert user is not None
        assert user.is_active

    @pytest.mark.parametrize(
        "code, status_code, detail",
        [
            ("000000", 403, "Код подтверждения неверный"),
            ("123456", 403, "Код подтверждения устарел"),
        ],
    )
    async def test_check_code_wrong_or_expired(self, ac, otp_dao, code, status_code, detail):
        phone = "+79990000004"

        await otp_dao.add(
            OtpAddSchema(
                phone=phone,
                code=code,
                expiration=datetime.now() + timedelta(minutes=1),
            )
        )

        response = await ac.post(
            "/app/v1/auth/sms/check_code/",
            json={"phone": phone, "code": code},
        )
        assert response.status_code == status_code
        assert response.json()["detail"] == detail

    async def test_check_code_blocked(self, ac, otp_dao):
        phone = "+79990000005"
        await otp_dao.add(
            OtpAddSchema(
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
        assert response.json()["detail"] == "Превышено число попыток ввода кода"
