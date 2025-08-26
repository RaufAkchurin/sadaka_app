from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import CommentsNotFoundException
from app.models.comment import Comment
from app.models.user import User
from app.v1.api_utils.pagination import Pagination, PaginationParams, PaginationResponseSchema
from app.v1.comment.schemas import CommentCreateDataSchema, CommentInfoSchema, CommentProjectFilterSchema, CommentSchema
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.users.dao import CommentDAO

v1_comment_router = APIRouter()


class CommentListUseCase:
    async def execute(self, session: AsyncSession, filtered_comments: list[CommentDAO]) -> list[CommentInfoSchema]:
        return [CommentInfoSchema.model_validate(project) for project in filtered_comments]


@v1_comment_router.post("/create", response_model=CommentInfoSchema)
async def create_comment(
    comment_data: CommentCreateDataSchema,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> CommentInfoSchema:
    new_comment: Comment = await CommentDAO(session=session).add(
        values=CommentSchema(user_id=user_data.id, project_id=comment_data.project_id, content=comment_data.content)
    )

    return CommentInfoSchema.model_validate(new_comment)


@v1_comment_router.get("/{project_id}", response_model=PaginationResponseSchema[CommentInfoSchema])
async def get_comments_by_project_id(
    project_id: int,
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> PaginationResponseSchema[CommentInfoSchema] | None:
    comments = await CommentDAO(session=session).find_all(filters=CommentProjectFilterSchema(project_id=project_id))

    comments_list_use_case = CommentListUseCase()
    serialized_comments = await comments_list_use_case.execute(session, comments)

    if comments is None or len(comments) == 0:
        raise CommentsNotFoundException

    if len(comments) > 0:
        return await Pagination.execute(serialized_comments, pagination.page, pagination.limit)
