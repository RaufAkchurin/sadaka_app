import pytest
from pydantic import BaseModel

from app.v1.project.dao import ProjectDAO
from app.v1.referrals.dao import ReferralDAO
from app.v1.users.dao import CityDAO, CommentDAO, OneTimePassDAO, PaymentDAO, RegionDAO, UserDAO


@pytest.fixture(scope="function")
async def region_dao(session) -> RegionDAO:
    region_dao = RegionDAO(session)
    return region_dao


@pytest.fixture(scope="function")
async def city_dao(session) -> CityDAO:
    city_dao = CityDAO(session)
    return city_dao


@pytest.fixture(scope="function")
async def user_dao(session) -> UserDAO:
    user_dao = UserDAO(session)
    return user_dao


@pytest.fixture(scope="function")
async def otp_dao(session) -> OneTimePassDAO:
    otp_dao = OneTimePassDAO(session)
    return otp_dao


@pytest.fixture(scope="function")
async def project_dao(session) -> ProjectDAO:
    project_dao = ProjectDAO(session)
    return project_dao


@pytest.fixture(scope="function")
async def comment_dao(session) -> CommentDAO:
    comment_dao = CommentDAO(session)
    return comment_dao


@pytest.fixture(scope="function")
async def payment_dao(session) -> PaymentDAO:
    payment_dao = PaymentDAO(session)
    return payment_dao


@pytest.fixture(scope="function")
async def referral_dao(session) -> ReferralDAO:
    referral_dao = ReferralDAO(session)
    return referral_dao


class DaoSchemas(BaseModel):
    region: RegionDAO
    city: CityDAO
    user: UserDAO
    otp: OneTimePassDAO
    project: ProjectDAO
    comment: CommentDAO
    payment: PaymentDAO
    referral: ReferralDAO

    class Config:
        arbitrary_types_allowed = True


@pytest.fixture(scope="function")
async def dao(session):
    return DaoSchemas(
        region=RegionDAO(session),
        city=CityDAO(session),
        user=UserDAO(session),
        otp=OneTimePassDAO(session),
        project=ProjectDAO(session),
        comment=CommentDAO(session),
        payment=PaymentDAO(session),
        referral=ReferralDAO(session),
    )
