from dataclasses import dataclass
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.dao.database import Base, str_uniq

# class LanguageEnum(Enum):
#     RUSSIAN = "Russian"
#     KAZAKH = "Kazakh"

@dataclass
class Country(Base):
    name: Mapped[str_uniq]
    language: Mapped[str]
    regions: Mapped[list["Region"]] = relationship(back_populates="region")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"


@dataclass
class Region(Base):
    name: Mapped[str_uniq]
    logo: Mapped[str]
    citys: Mapped[list["City"]] = relationship(back_populates="city")

    country_id: Mapped[int] = mapped_column(ForeignKey('countrys.id'), nullable=True)
    country: Mapped["Country"] = relationship("Country", back_populates="countrys", lazy="joined")



    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"


@dataclass
class City(Base):
    name: Mapped[str_uniq]
    users: Mapped[list["User"]] = relationship(back_populates="user")

    region_id: Mapped[int] = mapped_column(ForeignKey('citys.id'), nullable=True)
    region: Mapped["Region"] = relationship("Region", back_populates="citys", lazy="joined")


    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"