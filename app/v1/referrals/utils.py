from app.models.referral import Referral, ReferralTypeEnum
from app.settings import settings


async def generate_referral_link(referral: Referral):
    url = ""

    if referral.type == ReferralTypeEnum.FUND:
        url = f"{settings.get_base_url}app/v1/funds/detail/{referral.fund_id}"

    elif referral.type == ReferralTypeEnum.PROJECT:
        url = f"{settings.get_base_url}app/v1/projects/detail/{referral.project_id}"

    elif referral.type == ReferralTypeEnum.JOIN:
        url = "ADD URL TO DOWNLOAD APP IN BACKEND PLEASE"

    return url
