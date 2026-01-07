# utils/area_utils.py
"""
Offline-capable geospatial area calculations.

Uses pyproj and shapely to calculate the area of a
polygon defined by latitude and longitude coordinates.
"""

from typing import List, Dict
from pyproj import Geod
from shapely.geometry import Polygon

geod = Geod(ellps="WGS84")

def calculate_area_acres(polygon_latlon: List[Dict[str, float]]) -> float:
    """
    Calculates polygon area in acres from GPS coordinates.
    """
    try:
        if not polygon_latlon or len(polygon_latlon) < 3:
            return 0.0

        coords = [(p["lng"], p["lat"]) for p in polygon_latlon]
        polygon = Polygon(coords)

        if not polygon.is_valid:
            return 0.0

        lon, lat = zip(*coords)
        area_m2, _ = geod.polygon_area_perimeter(lon, lat)

        area_m2 = abs(area_m2)
        acres = area_m2 * 0.000247105
        return round(acres, 4)

    except Exception:
        return 0.0
