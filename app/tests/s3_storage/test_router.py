from uuid import uuid4

import pytest

from app.settings import settings


class TestS3Storage:
    @pytest.mark.parametrize(
        "is_authorized, status_code, response_message",
        [
            (True, 200, {"file_name": f"{settings.S3_FILE_BASE_URL}test_file.png"}),
            (False, 400, {"detail": "Токен отсутствует в заголовке"}),
        ],
    )
    async def test_upload_file(self, ac, auth_ac, is_authorized, status_code, response_message):
        file_content = b"Test file content"
        file_name = "test_file.png"

        if is_authorized:
            response = await auth_ac.client.post(
                "/s3_storage/upload",
                files={"file": (file_name, file_content, "image/png")},
                cookies=auth_ac.cookies.dict(),
            )
        else:
            response = await ac.post(
                "/s3_storage/upload",
                files={"file": (file_name, file_content, "image/png")},
            )

        assert response.status_code == status_code
        if is_authorized:
            assert response.json() == response_message
        else:
            assert response.json()["detail"] == "Токен отсутствует в заголовке"

    @pytest.mark.parametrize(
        "file_size, is_authorized, status_code, response_message",
        [
            (2 * 1024 * 1024, True, 400, {"detail": "Supported file size is 0 - 1 MB"}),
            (
                1024,
                True,
                200,
                {"file_name": f"{settings.S3_FILE_BASE_URL}test_file.png"},
            ),
            (2 * 1024 * 1024, False, 400, {"detail": "Токен отсутствует в заголовке"}),
        ],
    )
    async def test_upload_file_size(self, ac, auth_ac, file_size, is_authorized, status_code, response_message):
        file_content = b"a" * file_size  # Создаем файл с указанным размером
        file_name = "test_file.png"

        if is_authorized:
            response = await auth_ac.client.post(
                "/s3_storage/upload",
                files={"file": (file_name, file_content, "image/png")},
                cookies=auth_ac.cookies.dict(),
            )
        else:
            response = await ac.post(
                "/s3_storage/upload",
                files={"file": (file_name, file_content, "image/png")},
            )

        assert response.status_code == status_code
        assert response.json() == response_message

    @pytest.mark.parametrize(
        "file_type, is_authorized, status_code, response_message",
        [
            (
                "exe",
                True,
                400,
                {"detail": "Неподдерживаемый тип файла: exe. Поддерживаются только следующие типы png, jpg, pdf"},
            ),
            (
                "png",
                True,
                200,
                {"file_name": f"{settings.S3_FILE_BASE_URL}test_file.png"},
            ),
            ("exe", False, 400, {"detail": "Токен отсутствует в заголовке"}),
        ],
    )
    async def test_upload_file_type(self, ac, auth_ac, file_type, is_authorized, status_code, response_message):
        invalid_file_content = b"Invalid file content"
        file_name = f"test_file.{file_type}"

        if is_authorized:
            response = await auth_ac.client.post(
                "/s3_storage/upload",
                files={
                    "file": (
                        file_name,
                        invalid_file_content,
                        "application/octet-stream",
                    )
                },
                cookies=auth_ac.cookies.dict(),
            )
        else:
            response = await ac.post(
                "/s3_storage/upload",
                files={
                    "file": (
                        file_name,
                        invalid_file_content,
                        "application/octet-stream",
                    )
                },
            )

        assert response.status_code == status_code
        assert response.json() == response_message

    @pytest.mark.parametrize(
        "is_authorized, status_code, response_message",
        [
            (True, 200, b"Test file content"),
            (False, 400, {"detail": "Токен отсутствует в заголовке"}),
        ],
    )
    async def test_download_file(self, ac, auth_ac, is_authorized, status_code, response_message):
        file_name = "test_file.png"
        file_content = b"Test file content"

        # Сначала загрузим файл
        await auth_ac.client.post(
            "/s3_storage/upload",
            files={"file": (file_name, file_content, "image/png")},
            cookies=auth_ac.cookies.dict(),
        )

        if is_authorized:
            response = await auth_ac.client.get(f"/s3_storage/{file_name}", cookies=auth_ac.cookies.dict())
        else:
            response = await ac.get(f"/s3_storage/{file_name}")

        assert response.status_code == status_code
        if is_authorized:
            assert response.content == response_message
        else:
            assert response.json() == response_message

    @pytest.mark.parametrize(
        "is_authorized, file_name, status_code, response_message",
        [
            (True, f"{uuid4()}.png", 404, {"detail": "Файл не найден в хранилище S3"}),
            (False, f"{uuid4()}.png", 400, {"detail": "Токен отсутствует в заголовке"}),
        ],
    )
    async def test_download_file_not_found(self, ac, auth_ac, is_authorized, file_name, status_code, response_message):
        if is_authorized:
            response = await auth_ac.client.get(f"/s3_storage/{file_name}", cookies=auth_ac.cookies.dict())
        else:
            response = await ac.get(f"/s3_storage/{file_name}")

        assert response.status_code == status_code
        assert response.json() == response_message

    @pytest.mark.parametrize(
        "is_authorized, file_name, status_code, response_message",
        [
            (
                True,
                f"{settings.S3_FILE_BASE_URL}test_file.png",
                200,
                {"message": "Запрос на удаление файла отправлен."},
            ),
            (
                False,
                f"{settings.S3_FILE_BASE_URL}test_file.png",
                400,
                {"detail": "Токен отсутствует в заголовке"},
            ),
            (True, None, 400, {"detail": "Не передано название файла."}),
            (False, None, 400, {"detail": "Токен отсутствует в заголовке"}),
        ],
    )
    async def test_delete_file(self, ac, auth_ac, is_authorized, file_name, status_code, response_message):
        file_content = b"Test file content"

        # Сначала загрузим файл
        if is_authorized:
            await auth_ac.client.post(
                "/s3_storage/upload",
                files={"file": (file_name, file_content, "image/png")},
                cookies=auth_ac.cookies.dict(),
            )

        if is_authorized:
            delete_response = await auth_ac.client.delete(f"/s3_storage/{file_name}", cookies=auth_ac.cookies.dict())
        else:
            delete_response = await ac.delete(f"/s3_storage/{file_name}")

        assert delete_response.status_code == status_code
        assert delete_response.json() == response_message
