from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.exceptions import CommentNotFoundByIdException, CommentNotPermissionsException
from app.models.comment import Comment
from app.models.user import User
from app.v1.api_utils.pagination import Pagination, PaginationParams, PaginationResponseSchema
from app.v1.comment.schemas import (
    CommentContentSchema,
    CommentCreateDataSchema,
    CommentInfoSchema,
    CommentProjectFilterSchema,
    CommentSchema,
)
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.users.dao import CommentDAO
from app.v1.users.schemas import IdSchema

v1_comment_router = APIRouter()


@v1_comment_router.post("/create", response_model=CommentInfoSchema, status_code=status.HTTP_201_CREATED)
async def create_comment(
    payload: CommentCreateDataSchema,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> CommentInfoSchema:
    comment_dao = CommentDAO(session=session)
    new_comment: Comment = await comment_dao.add(
        values=CommentSchema(user_id=user_data.id, project_id=payload.project_id, content=payload.content)
    )

    return CommentInfoSchema.model_validate(new_comment)


@v1_comment_router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> None:
    comment_dao = CommentDAO(session=session)
    old_comment: Comment = await comment_dao.find_one_or_none_by_id(comment_id)

    if old_comment is None:
        raise CommentNotFoundByIdException

    if old_comment.user_id != user_data.id:
        raise CommentNotPermissionsException

    await comment_dao.delete(filters=IdSchema(id=comment_id))


@v1_comment_router.patch("/{comment_id}", response_model=CommentInfoSchema, status_code=status.HTTP_200_OK)
async def edit_comment(
    comment_id: int,
    payload: CommentContentSchema,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> CommentInfoSchema:
    comment_dao = CommentDAO(session=session)
    old_comment: Comment = await comment_dao.find_one_or_none_by_id(comment_id)

    if old_comment is None:
        raise CommentNotFoundByIdException

    if old_comment.user_id != user_data.id:
        raise CommentNotPermissionsException

    updated_comment = await comment_dao.update(
        filters=IdSchema(id=comment_id), values=CommentContentSchema(content=payload.content)
    )

    return CommentInfoSchema.model_validate(updated_comment)


@v1_comment_router.get(
    "/{project_id}", response_model=PaginationResponseSchema[CommentInfoSchema], status_code=status.HTTP_200_OK
)
async def get_comments_by_project_id(
    project_id: int,
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> PaginationResponseSchema[CommentInfoSchema] | None:
    comments = await CommentDAO(session=session).find_all(filters=CommentProjectFilterSchema(project_id=project_id))
    serialized_comments = [CommentInfoSchema.model_validate(c) for c in comments]

    return await Pagination.execute(serialized_comments, pagination.page, pagination.limit)
