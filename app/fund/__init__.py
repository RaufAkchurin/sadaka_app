# geo/__init__.py
from app.geo.v1.models import City, Country, Region

Region = Region
Country = Country
City = City

__all__ = ["Region", "Country", "City"]
