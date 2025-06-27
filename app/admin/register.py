from fastapi import FastAPI
from sqladmin import Admin

from app.admin.views.auth import MyAuthenticationBackend
from app.admin.views.city import CityAdmin
from app.admin.views.country import CountryAdmin
from app.admin.views.file import FileAdmin
from app.admin.views.fund import FundAdmin
from app.admin.views.payment import PaymentAdmin
from app.admin.views.project import ProjectAdmin
from app.admin.views.region import RegionAdmin
from app.admin.views.stage import StageAdmin
from app.admin.views.user import UserAdmin
from app.settings import settings
from app.v1.dao.database import engine


def create_admin_panel(app: FastAPI):
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=MyAuthenticationBackend(secret_key=settings.SECRET_KEY),
        title=f"Садака app админка {settings.MODE}",
        logo_url="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
        debug=True,  # Enable debug mode for better error reporting
    )

    admin.add_view(CountryAdmin)
    admin.add_view(RegionAdmin)
    admin.add_view(CityAdmin)

    admin.add_view(UserAdmin)

    admin.add_view(FundAdmin)
    admin.add_view(ProjectAdmin)
    admin.add_view(StageAdmin)
    admin.add_view(FileAdmin)

    admin.add_view(PaymentAdmin)
