from app.models.file import File
from app.models.fund import Fund
from app.models.geo import City, Country, Region
from app.models.payments import Payment
from app.models.project import Project, Stage
from app.models.user import User
from app.v1.dao.base import BaseDAO


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
