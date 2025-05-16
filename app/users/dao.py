from app.dao.base import BaseDAO
from app.file.models import File
from app.fund.models import Fund
from app.geo.models import City, Country, Region
from app.payments.models import Payment
from app.project.models import Project, Stage
from app.users.models import User


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
