from admin.views.auth import get_token_payload
from sqladmin import ModelView
from starlette.requests import Request


class SuperAdminPerm(ModelView):
    def is_accessible(self, request: Request) -> bool:
        payload = get_token_payload(request)
        if payload.user_role in ["superuser"]:
            return True
        else:
            return False


class FundAdminAccess(ModelView):
    def is_accessible(self, request: Request) -> bool:
        payload = get_token_payload(request)

        if payload.user_role in ["superuser", "fund_admin"]:
            return True
        else:
            return False
