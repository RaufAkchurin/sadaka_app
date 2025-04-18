from fastapi import FastAPI
from sqladmin import Admin

from admin.views import (
    CityAdmin,
    CountryAdmin,
    DocumentAdmin,
    FundAdmin,
    ProjectAdmin,
    RegionAdmin,
    RoleAdmin,
    StageAdmin,
    UserAdmin,
)
from app.dao.database import engine


def create_admin_panel(app: FastAPI):
    admin = Admin(app, engine)

    admin.add_view(CountryAdmin)
    admin.add_view(RegionAdmin)
    admin.add_view(CityAdmin)

    admin.add_view(RoleAdmin)
    admin.add_view(UserAdmin)

    admin.add_view(FundAdmin)
    admin.add_view(ProjectAdmin)
    admin.add_view(StageAdmin)
    admin.add_view(DocumentAdmin)
