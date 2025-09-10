from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ReferralGenPayloadException
from app.models.referral import ReferralTypeEnum
from app.models.user import User
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.users.dao import ReferralDAO

v1_referral_router = APIRouter()


class ReferralKeyResponseSchema(BaseModel):
    key: str
    model_config = ConfigDict(from_attributes=True)


class ReferralAddSchema(BaseModel):
    entity_type: ReferralTypeEnum
    entity_id: int | None
    sharer_id: int


async def referral_generation_payload_validator(entity_type: ReferralTypeEnum, entity_id: int | None) -> None:
    if entity_type.value in ["fund", "project"] and entity_id is None:
        raise ReferralGenPayloadException


@v1_referral_router.get("/generate_code")
async def get_referral_code(
    entity_type: ReferralTypeEnum,
    entity_id: int = Query(default=None, alias="entity_id"),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> ReferralKeyResponseSchema | None:
    await referral_generation_payload_validator(entity_type, entity_id)

    referral_dao = ReferralDAO(session=session)
    if entity_type == ReferralTypeEnum.JOIN:
        referral = await referral_dao.add(
            values=ReferralAddSchema(
                entity_type=entity_type,
                entity_id=entity_id,
                sharer_id=user_data.id,
            )
        )
        return ReferralKeyResponseSchema(key=referral.key)
