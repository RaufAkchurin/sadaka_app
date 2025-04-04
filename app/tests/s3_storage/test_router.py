import pytest
from app.tests.conftest import auth_by  # Предполагаю, что эта функция существует для авторизации
from uuid import uuid4


class TestFileUpload:

    @pytest.mark.parametrize("is_authorized, status_code, response_message",
                             [
                                 (True, 200, {'file_name': 'test_file.png'}),
                                 (False, 400, {"detail": "Токен отсутствует в заголовке"}),
                             ])
    async def test_upload_file(self, ac, auth_ac, is_authorized, status_code, response_message):
        file_content = b"Test file content"
        file_name = f"{uuid4()}.png"

        if is_authorized:
            response = await auth_ac.client.post(
                "/s3_storage/upload",
                files={"file": (file_name, file_content, "image/png")},
                cookies=auth_ac.cookies.dict()
            )
        else:
            response = await ac.post(
                "/s3_storage/upload",
                files={"file": (file_name, file_content, "image/png")}
            )

        assert response.status_code == status_code
        if is_authorized:
            assert response.json() == response_message
        else:
            assert response.json()["detail"] == "Токен отсутствует в заголовке"


    @pytest.mark.parametrize("file_size, is_authorized, status_code, response_message",
                             [
                                 (2 * 1024 * 1024, True, 400, "Supported file size is 0 - 1 MB"),
                                 (1024, True, 200, {'file_name': 'test_file.png'}),
                                 (2 * 1024 * 1024, False, 400, {"detail": "Токен отсутствует в заголовке"}),
                             ])
    async def test_upload_file_size(self, ac, auth_ac, file_size, is_authorized, status_code, response_message):
        file_content = b"a" * file_size  # Создаем файл с указанным размером
        file_name = f"{uuid4()}.png"

        if is_authorized:
            response = await auth_ac.client.post(
                "/s3_storage/upload",
                files={"file": (file_name, file_content, "image/png")},
                cookies=auth_ac.cookies.dict()
            )
        else:
            response = await ac.post(
                "/s3_storage/upload",
                files={"file": (file_name, file_content, "image/png")}
            )

        assert response.status_code == status_code
        assert response.json()["detail"] == response_message


    @pytest.mark.parametrize("file_type, is_authorized, status_code, response_message",
                             [
                                 ("exe", True, 400, "Неподдерживаемый тип файла: application/octet-stream. Поддерживаются только следующие типы image/png, image/jpeg, application/pdf"),
                                 ("png", True, 200, {'file_name': 'test_file.png'}),
                                 ("exe", False, 400, {"detail": "Токен отсутствует в заголовке"}),
                             ])
    async def test_upload_file_type(self, ac, auth_ac, file_type, is_authorized, status_code, response_message):
        invalid_file_content = b"Invalid file content"
        file_name = f"{uuid4()}.{file_type}"

        if is_authorized:
            response = await auth_ac.client.post(
                "/s3_storage/upload",
                files={"file": (file_name, invalid_file_content, "application/octet-stream")},
                cookies=auth_ac.cookies.dict()
            )
        else:
            response = await ac.post(
                "/s3_storage/upload",
                files={"file": (file_name, invalid_file_content, "application/octet-stream")}
            )

        assert response.status_code == status_code
        assert response.json()["detail"] == response_message


class TestFileDownload:

    @pytest.mark.parametrize("is_authorized, status_code, response_message",
                             [
                                 (True, 200, b"Test file content"),
                                 (False, 400, {"detail": "Токен отсутствует в заголовке"}),
                             ])
    async def test_download_file(self, ac, auth_ac, is_authorized, status_code, response_message):
        file_name = "test_file.png"
        file_content = b"Test file content"

        # Сначала загрузим файл
        if is_authorized:
            await auth_ac.client.post(
                "/s3_storage/upload",
                files={"file": (file_name, file_content, "image/png")},
                cookies=auth_ac.cookies.dict()
            )
        else:
            await ac.post(
                "/s3_storage/upload",
                files={"file": (file_name, file_content, "image/png")}
            )

        if is_authorized:
            response = await auth_ac.client.get(
                f"/s3_storage/download?file_name={file_name}",
                cookies=auth_ac.cookies.dict()
            )
        else:
            response = await ac.get(f"/s3_storage/download?file_name={file_name}")

        assert response.status_code == status_code
        if is_authorized:
            assert response.content == response_message
        else:
            assert response.json()["detail"] == "Токен отсутствует в заголовке"


    @pytest.mark.parametrize("is_authorized, file_name, status_code, response_message",
                             [
                                 (True, "non_existent_file.png", 404, "File not found."),
                                 (False, "non_existent_file.png", 400, {"detail": "Токен отсутствует в заголовке"}),
                             ])
    async def test_download_file_not_found(self, ac, auth_ac, is_authorized, file_name, status_code, response_message):
        if is_authorized:
            response = await auth_ac.client.get(f"/s3_storage/download?file_name={file_name}", cookies=auth_ac.cookies.dict())
        else:
            response = await ac.get(f"/s3_storage/download?file_name={file_name}")

        assert response.status_code == status_code
        assert response.json() == response_message


class TestFileDelete:

    @pytest.mark.parametrize("is_authorized, file_name, status_code, response_message",
                             [
                                 (True, "test_file.png", 200, {'message': 'Файл успешно удалён.'}),
                                 (False, "test_file.png", 400, {"detail": "Токен отсутствует в заголовке"}),
                             ])
    async def test_delete_file(self, ac, auth_ac, is_authorized, file_name, status_code, response_message):
        file_content = b"Test file content"

        # Сначала загрузим файл
        if is_authorized:
            await auth_ac.client.post(
                "/s3_storage/upload",
                files={"file": (file_name, file_content, "image/png")},
                cookies=auth_ac.cookies.dict()
            )
        else:
            await ac.post(
                "/s3_storage/upload",
                files={"file": (file_name, file_content, "image/png")}
            )

        if is_authorized:
            response = await auth_ac.client.delete(
                f"/s3_storage/delete?file_name={file_name}",
                cookies=auth_ac.cookies.dict()
            )
        else:
            response = await ac.delete(f"/s3_storage/delete?file_name={file_name}")

        assert response.status_code == status_code
        assert response.json() == response_message


    @pytest.mark.parametrize("is_authorized, file_name, status_code, response_message",
                             [
                                 (True, None, 400, {'detail': 'File name not provided.'}),
                                 (False, None, 400, {"detail": "Токен отсутствует в заголовке"}),
                             ])
    async def test_delete_file_no_name(self, ac, auth_ac, is_authorized, file_name, status_code, response_message):
        if is_authorized:
            response = await auth_ac.client.delete(f"/s3_storage/delete?file_name={file_name}", cookies=auth_ac.cookies.dict())
        else:
            response = await ac.delete(f"/s3_storage/delete?file_name={file_name}")

        assert response.status_code == status_code
        assert response.json() == response_message
