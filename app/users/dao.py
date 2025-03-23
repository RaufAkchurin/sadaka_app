from app.dao.base import BaseDAO
from app.users.models import User, Role


class UsersDAO(BaseDAO):
    model = User

class RoleDAO(BaseDAO):
    model = Role
