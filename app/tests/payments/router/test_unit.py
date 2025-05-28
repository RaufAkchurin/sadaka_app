from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from models.project import Project
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from v1.payment.enums import PaymentStatusEnum
from v1.payment.schemas import YooWebhookDataSchema
from v1.payment.use_cases.callback import YooCallbackSuccessUseCaseImpl


class TestYookassaClientIpSecurityChecker:
    async def test_ip_in_range(self):
        request = AsyncMock()
        request.client.host = "185.71.76.1"

        use_case = YooCallbackSuccessUseCaseImpl(request, AsyncMock())
        try:
            await use_case._YooCallbackSuccessUseCaseImpl__yookassa_client_ip_security_checker()
        except HTTPException:
            pytest.fail("Unexpected YookassaCallbackForbiddenException")

    async def test_ip_not_in_range(self):
        request = AsyncMock()
        request.client.host = "192.168.1.1"

        use_case = YooCallbackSuccessUseCaseImpl(request, AsyncMock())

        with pytest.raises(HTTPException):
            await use_case._YooCallbackSuccessUseCaseImpl__yookassa_client_ip_security_checker()

    # async def test_execute_success(self, mocker):
    #     # Создаем моки для зависимостей
    #     request = AsyncMock(spec=Request)
    #     session = AsyncMock(spec=AsyncSession)
    #
    #     # Создаем экземпляр класса
    #     use_case = YooCallbackSuccessUseCaseImpl(request, session)
    #
    #     # Мокируем методы
    #     use_case._YooCallbackSuccessUseCaseImpl__create_payment_in_db = AsyncMock()
    #     use_case._YooCallbackSuccessUseCaseImpl__yookassa_client_ip_security_checker = AsyncMock()
    #
    #     # Вызываем метод execute
    #     await use_case.execute()
    #
    #     # Проверяем, что методы были вызваны
    #     use_case._YooCallbackSuccessUseCaseImpl__create_payment_in_db.assert_awaited_once()
    #     use_case._YooCallbackSuccessUseCaseImpl__yookassa_client_ip_security_checker.assert_awaited_once()

    # async def test_create_payment_in_db_success(self, mocker):
    #     # Создаем моки для зависимостей
    #     request = AsyncMock(spec=Request)
    #     session = AsyncMock(spec=AsyncSession)
    #
    #     # Создаем экземпляр класса
    #     use_case = YooCallbackSuccessUseCaseImpl(request, session)
    #
    #     # Мокируем методы
    #     use_case._YooCallbackSuccessUseCaseImpl__get_webhook_data_object = AsyncMock(return_value=YooWebhookDataSchema(
    #         id="test_id",
    #         amount=MagicMock(value=100),
    #         income_amount=MagicMock(value=90),
    #         test=False,
    #         status=PaymentStatusEnum.SUCCEEDED,
    #         metadata=MagicMock(user_id="user_id", project_id="project_id"),
    #         created_at="2023-01-01T00:00:00",
    #         captured_at="2023-01-01T00:00:00"
    #     ))
    #
    #     use_case._YooCallbackSuccessUseCaseImpl__get_project = AsyncMock(return_value=Project(active_stage_number=1))
    #
    #     payment_dao_mock = AsyncMock()
    #     payment_dao_mock.add = AsyncMock()
    #     mocker.patch('your_module.PaymentDAO',
    #                  return_value=payment_dao_mock)  # Замените your_module на имя вашего модуля
    #
    #     # Вызываем метод __create_payment_in_db
    #     await use_case._YooCallbackSuccessUseCaseImpl__create_payment_in_db()
    #
    #     # Проверяем, что метод add был вызван
    #     payment_dao_mock.add.assert_awaited_once()
    #
    # async def test_yookassa_client_ip_security_checker_success():
    #     # Создаем моки для зависимостей
    #     request = AsyncMock(spec=Request)
    #     request.client.host = "185.71.76.1"
    #     session = AsyncMock(spec=AsyncSession)
    #
    #     # Создаем экземпляр класса
    #     use_case = YooCallbackSuccessUseCaseImpl(request, session)
    #
    #     # Вызываем метод __yookassa_client_ip_security_checker
    #     await use_case._YooCallbackSuccessUseCaseImpl__yookassa_client_ip_security_checker()
    #
    #     # Если не было выброшено исключение, тест прошел успешно
    #
    # async def test_yookassa_client_ip_security_checker_forbidden():
    #     # Создаем моки для зависимостей
    #     request = AsyncMock(spec=Request)
    #     request.client.host = "192.168.1.1"
    #     session = AsyncMock(spec=AsyncSession)
    #
    #     # Создаем экземпляр класса
    #     use_case = YooCallbackSuccessUseCaseImpl(request, session)
    #
    #     # Проверяем, что будет выброшено исключение
    #     with pytest.raises(YookassaCallbackForbiddenException):
    #         await use_case._YooCallbackSuccessUseCaseImpl__yookassa_client_ip_security_checker()
    #
    # async def test_get_webhook_data_object_success(mocker):
    #     # Создаем моки для зависимостей
    #     request = AsyncMock(spec=Request)
    #     request.body = AsyncMock(
    #         return_value=b'{"object": {"id": "test_id", "amount": {"value": 100}, "income_amount": {"value": 90}, "test": false, "status": "succeeded", "metadata": {"user_id": "user_id", "project_id": "project_id"}, "created_at": "2023-01-01T00:00:00", "captured_at": "2023-01-01T00:00:00"}}')
    #     session = AsyncMock(spec=AsyncSession)
    #
    #     # Создаем экземпляр класса
    #     use_case = YooCallbackSuccessUseCaseImpl(request, session)
    #
    #     # Вызываем метод __get_webhook_data_object
    #     result = await use_case._YooCallbackSuccessUseCaseImpl__get_webhook_data_object()
    #
    #     # Проверяем, что результат соответствует ожидаемому
    #     assert result.id == "test_id"
    #     assert result.amount.value == 100
    #     assert result.income_amount.value == 90
    #     assert result.test is False
    #     assert result.status == PaymentStatusEnum.SUCCEEDED
    #     assert result.metadata.user_id == "user_id"
    #     assert result.metadata.project_id == "project_id"
    #     assert result.created_at == "2023-01-01T00:00:00"
    #     assert result.captured_at == "2023-01-01T00:00:00"
    #
    # async def test_get_project_success(mocker):
    #     # Создаем моки для зависимостей
    #     request = AsyncMock(spec=Request)
    #     session = AsyncMock(spec=AsyncSession)
    #
    #     # Создаем экземпляр класса
    #     use_case = YooCallbackSuccessUseCaseImpl(request, session)
    #
    #     # Мокируем методы
    #     use_case._YooCallbackSuccessUseCaseImpl__get_webhook_data_object = AsyncMock(return_value=YooWebhookDataSchema(
    #         id="test_id",
    #         amount=MagicMock(value=100),
    #         income_amount=MagicMock(value=90),
    #         test=False,
    #         status=PaymentStatusEnum.SUCCEEDED,
    #         metadata=MagicMock(user_id="user_id", project_id="project_id"),
    #         created_at="2023-01-01T00:00:00",
    #         captured_at="2023-01-01T00:00:00"
    #     ))
    #
    #     project_dao_mock = AsyncMock()
    #     project_dao_mock.find_one_or_none_by_id = AsyncMock(return_value=Project(active_stage_number=1))
    #     mocker.patch('your_module.ProjectDAO',
    #                  return_value=project_dao_mock)  # Замените your_module на имя вашего модуля
    #
    #     # Вызываем метод __get_project
    #     result = await use_case._YooCallbackSuccessUseCaseImpl__get_project()
    #
    #     # Проверяем, что результат соответствует ожидаемому
    #     assert result.active_stage_number == 1

    # async def test_use_case_complete(self):
    #     request = AsyncMock()
    #     request.client.host = "185.71.76.1"
    #     request.json = callback_mock_success
    #
    #     use_case = YooCallbackSuccessUseCaseImpl(request, AsyncMock())
    #     await use_case.execute()
    #
    #     session_gen = get_session_with_commit()
    #     session = await session_gen.__anext__()
    #     payment_dao = PaymentDAO(session=session)
    #     payments: list[Payment] = await payment_dao.find_all()
    #
    #     city_dao = CityDAO(session=session)
    #     cities: list[City] = await city_dao.find_all()
    #
    #     assert len(payments) == 1
