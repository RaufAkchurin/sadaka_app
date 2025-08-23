from dataclasses import dataclass

from sqlalchemy import Column
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String, Table, event, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.city import City
from app.models.payment import Payment
from app.v1.auth.service_jwt import hash_password_in_signal
from app.v1.dao.database import Base
from app.v1.users.enums import LanguageEnum, RoleEnum

user_fund_access = Table(
    "user_fund_access",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("fund_id", Integer, ForeignKey("funds.id")),
)


@dataclass
class User(Base):
    name: Mapped[str | None]
    password: Mapped[str | None]
    google_access_token: Mapped[str | None]

    phone: Mapped[str | None] = mapped_column(String(11), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)

    language: Mapped[LanguageEnum] = mapped_column(
        SqlEnum(LanguageEnum, name="language_enum"),
        server_default=LanguageEnum.RU.value,
        default=LanguageEnum.RU.value,
        nullable=False,
    )

    funds_access: Mapped[list["Fund"]] = relationship(  # noqa F821
        secondary=user_fund_access,
        back_populates="user_have_access",
        lazy="selectin",
    )

    role: Mapped[RoleEnum] = mapped_column(
        SqlEnum(RoleEnum, name="role_enum"),
        server_default="USER",
        default="USER",
        nullable=False,
    )

    is_anonymous: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    picture_id: Mapped[int | None] = mapped_column(ForeignKey("files.id"), nullable=True, unique=True, default=None)
    picture: Mapped["File | None"] = relationship(  # noqa F821
        "File",  # noqa F821
        back_populates="user_picture",
        lazy="joined",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    # Связь с городом
    city_id: Mapped[int] = mapped_column(ForeignKey("citys.id"), default=1, server_default=text("1"))
    city: Mapped["City"] = relationship("City", back_populates="users", lazy="joined")

    # RELATIONS
    payments: Mapped[list["Payment"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @property
    def picture_url(self) -> str | None:
        return self.picture.url if self.picture else None

    @property
    def funds_access_ids(self) -> list[int]:
        return [fund.id for fund in self.funds_access]


# def _ensure_contact(mapper, connection, target: User):
#     """ORM-валидация перед INSERT/UPDATE: нужен хотя бы один из email/phone."""
#     if not (target.email and target.email.strip()) and not (target.phone and target.phone.strip()):
#         # Любое исключение прервёт flush/commit
#         raise ValueError("У пользователя должен быть указан email или phone (хотя бы одно поле).")
#
#
# # Подвязываем на insert/update
# event.listen(User, "before_insert", _ensure_contact)
# event.listen(User, "before_update", _ensure_contact)


# всегда хешируем пароль, привязываем событие перед вставкой или обновлением
event.listen(User.password, "set", hash_password_in_signal, retval=True)
