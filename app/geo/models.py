from dataclasses import dataclass

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dao.database import Base, str_uniq


@dataclass
class Country(Base):
    name: Mapped[str_uniq]
    language: Mapped[str]

    # Связь с регионами
    regions: Mapped[list["Region"]] = relationship("Region", back_populates="country")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"



@dataclass
class Region(Base):
    name: Mapped[str_uniq]
    logo: Mapped[str]

    # Внешний ключ для страны
    country_id: Mapped[int] = mapped_column(ForeignKey('countrys.id'), nullable=True)
    country: Mapped["Country"] = relationship("Country", back_populates="regions", lazy="joined")

    # Связь с городами
    citys: Mapped[list["City"]] = relationship("City", back_populates="region")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"



@dataclass
class City(Base):
    name: Mapped[str_uniq]

    # Связь с пользователями
    users: Mapped[list["User"]] = relationship("User", back_populates="city")

    # Внешний ключ для региона
    region_id: Mapped[int] = mapped_column(ForeignKey('regions.id'), nullable=True)
    region: Mapped["Region"] = relationship("Region", back_populates="citys", lazy="joined")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

