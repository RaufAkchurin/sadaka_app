from app.models.city import City
from app.models.country import Country
from app.models.file import File
from app.models.fund import Fund
from app.models.one_time_pass import OneTimePass
from app.models.payment import Payment
from app.models.project import Project
from app.models.region import Region
from app.models.stage import Stage
from app.models.user import User
from app.v1.dao.base import BaseDAO


class UserDAO(BaseDAO):
    model = User

class OneTimePassDAO(BaseDAO):
    model = OneTimePass


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
