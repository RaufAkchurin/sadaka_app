import asyncio
import time

import pytest
from loguru import logger


class TestProjectDetail:
    async def test_400_authorization(self, ac) -> None:
        response = await ac.get("/app/v1/projects/detail/1")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_id_validate(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.get("/app/v1/projects/detail/hob", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "input": "hob",
                    "loc": ["path", "project_id"],
                    "msg": "Input should be a valid integer, unable to parse string as an integer",
                    "type": "int_parsing",
                }
            ]
        }

    async def test_id_not_exist(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.get("/app/v1/projects/detail/99", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 404

    async def test_list_active(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.get("/app/v1/projects/detail/1", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 200

        assert response.json() == {
            "active_stage_number": 2,
            "collected_percentage": 20,
            "description": "desc1",
            "documents": [
                {
                    "id": 1,
                    "mime": "PDF",
                    "name": "Док1 для Проекта 1",
                    "size": 123,
                    "type": "DOCUMENT",
                    "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F1.png",
                },
                {
                    "id": 2,
                    "mime": "PDF",
                    "name": "Док2 для Проекта 1",
                    "size": 123,
                    "type": "DOCUMENT",
                    "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F2.png",
                },
            ],
            "fund": {"id": 1, "name": "fund1", "picture_url": None},
            "goal": 10000,
            "id": 1,
            "name": "project1",
            "pictures_list": [],
            "region": {
                "name": "Tatarstan",
                "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F4.png",
            },
            "stages": [
                {
                    "collected": 2000,
                    "goal": 4000,
                    "name": "proj1 stage1",
                    "number": 1,
                    "reports": [
                        {
                            "id": 5,
                            "mime": "PDF",
                            "name": "Реп1 для Стадии 1",
                            "size": 123,
                            "type": "REPORT",
                            "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F5.png",
                        },
                        {
                            "id": 6,
                            "mime": "PDF",
                            "name": "Реп2 для Стадии 1",
                            "size": 123,
                            "type": "REPORT",
                            "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F6.png",
                        },
                    ],
                    "status": "finished",
                },
                {
                    "collected": 3000,
                    "goal": 5000,
                    "name": "proj1 stage2",
                    "number": 2,
                    "reports": [
                        {
                            "id": 7,
                            "mime": "PDF",
                            "name": "Реп1 для Стадии 2",
                            "size": 123,
                            "type": "REPORT",
                            "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F7.png",
                        },
                        {
                            "id": 8,
                            "mime": "PDF",
                            "name": "Реп2 для Стадии 2",
                            "size": 123,
                            "type": "REPORT",
                            "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F8.png",
                        },
                    ],
                    "status": "active",
                },
            ],
            "status": "active",
            "total_income": 2000,
            "unique_sponsors": 1,
        }

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(200, 70, 115)])
    async def test_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get("/app/v1/projects/detail/1", cookies=auth_ac_super.cookies.dict())
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        # необязательная проверка минимального порога
        assert rps > expected_rps

        # необязательная проверка максимального порога
        assert rps < max_rps
