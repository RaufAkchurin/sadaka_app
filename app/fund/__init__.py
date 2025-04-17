# geo/__init__.py
from app.geo.models import Region, Country, City

Region = Region
Country = Country
City = City

__all__ = ["Region", "Country", "City"]