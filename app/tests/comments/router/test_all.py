import asyncio
import time

import pytest
from loguru import logger

from app.models.comment import Comment
from app.v1.comment.schemas import (
    CommentContentSchema,
    CommentCreateDataSchema,
    CommentProjectFilterSchema,
    CommentSchema,
)


class TestCommentsAPI:
    @pytest.mark.parametrize(
        "payload, status_code",
        [
            ({"project_id": 1, "content": "hello world"}, 201),
        ],
    )
    async def test_create_comment(self, auth_ac_super, comment_dao, payload, status_code):
        resp = await auth_ac_super.client.post(
            "/app/v1/comments/",
            json=payload,
            cookies=auth_ac_super.cookies.dict(),
        )
        assert resp.status_code == status_code

        data = resp.json()
        assert data["project_id"] == payload["project_id"]
        assert data["content"] == payload["content"]
        assert "id" in data

        rows = await comment_dao.find_all(filters=CommentProjectFilterSchema(project_id=payload["project_id"]))
        assert any(r.content == payload["content"] for r in rows)

    async def test_delete_comment_success(self, auth_ac_super, comment_dao):
        created = await auth_ac_super.client.post(
            "/app/v1/comments/",
            json=CommentCreateDataSchema(project_id=201, content="to be deleted").model_dump(),
            cookies=auth_ac_super.cookies.dict(),
        )
        assert created.status_code == 201
        comment_id = created.json()["id"]

        resp = await auth_ac_super.client.delete(
            f"/app/v1/comments/{comment_id}",
            cookies=auth_ac_super.cookies.dict(),
        )
        assert resp.status_code == 204

        deleted = await comment_dao.find_one_or_none_by_id(comment_id)
        assert deleted is None

    async def test_delete_comment_not_found(self, auth_ac_super):
        resp = await auth_ac_super.client.delete(
            "/app/v1/comments/99999999",
            cookies=auth_ac_super.cookies.dict(),
        )
        assert resp.status_code == 404  # CommentNotFoundByIdException

    async def test_delete_comment_forbidden(self, auth_ac_super, comment_dao):
        foreign = await comment_dao.add_and_commit_for_tests(
            values=CommentSchema(user_id=999999, project_id=301, content="foreign")
        )
        resp = await auth_ac_super.client.delete(
            f"/app/v1/comments/{foreign}",
            cookies=auth_ac_super.cookies.dict(),
        )
        assert resp.status_code == 403  # CommentNotPermissionsException

        still_there = await comment_dao.find_one_or_none_by_id(foreign)
        assert still_there is not None

    async def test_edit_comment_success(self, auth_ac_super, comment_dao):
        created = await auth_ac_super.client.post(
            "/app/v1/comments/",
            json=CommentCreateDataSchema(project_id=401, content="old").model_dump(),
            cookies=auth_ac_super.cookies.dict(),
        )
        assert created.status_code == 201
        comment_id = created.json()["id"]

        payload = CommentContentSchema(content="new content")
        resp = await auth_ac_super.client.patch(
            f"/app/v1/comments/{comment_id}",
            json=payload.model_dump(),
            cookies=auth_ac_super.cookies.dict(),
        )
        assert resp.status_code == 200

        updated: Comment = await comment_dao.find_one_or_none_by_id(comment_id)
        assert updated is not None
        assert updated.content == "new content"

    async def test_edit_comment_not_found(self, auth_ac_super):
        resp = await auth_ac_super.client.patch(
            "/app/v1/comments/99999999",
            json=CommentContentSchema(content="x").model_dump(),
            cookies=auth_ac_super.cookies.dict(),
        )
        assert resp.status_code == 404  # CommentNotFoundByIdException

    async def test_edit_comment_forbidden(self, auth_ac_super, comment_dao):
        foreign = await comment_dao.add_and_commit_for_tests(
            values=CommentSchema(user_id=999999, project_id=501, content="locked")
        )
        resp = await auth_ac_super.client.patch(
            f"/app/v1/comments/{foreign}",
            json=CommentContentSchema(content="try edit").model_dump(),
            cookies=auth_ac_super.cookies.dict(),
        )
        assert resp.status_code == 403  # CommentNotPermissionsException

        same: Comment = await comment_dao.find_one_or_none_by_id(data_id=foreign)
        assert same is not None
        assert same.content == "locked"

    async def test_get_comments_by_project_id_empty(self, auth_ac_super):
        project_id = 2
        resp = await auth_ac_super.client.get(
            f"/app/v1/comments/{project_id}",
            params={"project_id": project_id, "page": 1, "limit": 10},
            cookies=auth_ac_super.cookies.dict(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("state").get("page") == 1
        assert data.get("state").get("size") == 10
        assert data.get("state").get("total_pages") == 1
        assert data.get("state").get("total_items") == 2

    async def test_get_comments_by_project_id_paginated(self, auth_ac_super, comment_dao):
        project_id = 1
        for i in range(15):
            await comment_dao.add_and_commit_for_tests(
                values=CommentSchema(user_id=1, project_id=project_id, content=f"c{i}")
            )

        resp1 = await auth_ac_super.client.get(
            f"/app/v1/comments/{project_id}",
            params={"project_id": project_id, "page": 1, "limit": 10},
            cookies=auth_ac_super.cookies.dict(),
        )
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1.get("state").get("page") == 1
        assert data1.get("state").get("size") == 10
        assert data1.get("state").get("total_pages") == 2
        assert data1.get("state").get("total_items") == 17
        assert len(data1["items"]) == 10

        resp2 = await auth_ac_super.client.get(
            f"/app/v1/comments/{project_id}",
            params={"project_id": project_id, "page": 2, "limit": 10},
            cookies=auth_ac_super.cookies.dict(),
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2.get("state").get("page") == 2
        assert data2.get("state").get("size") == 10
        assert data2.get("state").get("total_pages") == 2
        assert data2.get("state").get("total_items") == 17
        assert len(data2["items"]) == 7

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(400, 260, 330)])
    async def test_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            resp1 = await auth_ac_super.client.get(
                "/app/v1/comments/1",
                params={"project_id": 1, "page": 1, "limit": 10},
                cookies=auth_ac_super.cookies.dict(),
            )
            assert resp1.status_code == 200
            return resp1

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        # необязательная проверка минимального порога
        assert rps > expected_rps

        # необязательная проверка максимального порога (чтобы видеть прирост, который не ожидал)
        assert rps < max_rps
