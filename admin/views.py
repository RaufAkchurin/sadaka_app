from sqladmin import ModelView

from app.documents.models import Document
from app.fund import City, Country, Region
from app.fund.models import Fund
from app.payments.models import Payment
from app.project.models import Project, Stage
from app.users.models import Role, User


class BaseView(ModelView):
    form_excluded_columns = [User.created_at, User.updated_at]


############### USERS ############### # noqa


class RoleAdmin(BaseView, model=Role):
    column_list = [Role.id, Role.name]


class UserAdmin(BaseView, model=User):
    column_list = [User.id, User.name]


############### GEO ############### # noqa


class CityAdmin(BaseView, model=City):
    column_list = [City.id, City.name]


class RegionAdmin(BaseView, model=Region):
    column_list = [Region.id, Region.name]


class CountryAdmin(BaseView, model=Country):
    column_list = [Country.id, Country.name]


############### CORE CHARITY ############### # noqa


class FundAdmin(BaseView, model=Fund):
    column_list = [Fund.id, Fund.name]


class ProjectAdmin(BaseView, model=Project):
    column_list = [Project.id, Project.name]


class StageAdmin(BaseView, model=Stage):
    column_list = [Stage.id, Stage.name]


class DocumentAdmin(BaseView, model=Document):
    column_list = [Document.id, Document.name]


############### PAYMENTS ############### # noqa


class PaymentAdmin(BaseView, model=Payment):
    column_list = [Payment.id]
