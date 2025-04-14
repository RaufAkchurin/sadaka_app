from app.dao.base import BaseDAO
from app.geo.models import City, Country, Region
from app.users.models import Role, User


class UsersDAO(BaseDAO):
    model = User


class RoleDAO(BaseDAO):
    model = Role


class CityDAO(BaseDAO):
    model = City


class RegionDAO(BaseDAO):
    model = Region


class CountryDAO(BaseDAO):
    model = Country
