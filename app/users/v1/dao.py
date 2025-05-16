from app.dao.v1.base import BaseDAO
from app.file.v1.models import File
from app.fund.v1.models import Fund
from app.geo.v1.models import City, Country, Region
from app.payments.v1.models import Payment
from app.project.v1.models import Project, Stage
from app.users.v1.models import User


class UserDAO(BaseDAO):
    model = User


class CountryDAO(BaseDAO):
    model = Country


class CityDAO(BaseDAO):
    model = City


class RegionDAO(BaseDAO):
    model = Region


class FundDAO(BaseDAO):
    model = Fund


class ProjectDAO(BaseDAO):
    model = Project


class StageDAO(BaseDAO):
    model = Stage


class FileDAO(BaseDAO):
    model = File


class PaymentDAO(BaseDAO):
    model = Payment
