# geo/__init__.py
from models.geo import City, Country, Region

Region = Region
Country = Country
City = City

__all__ = ["Region", "Country", "City"]
