#### app/utils.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import math

async def filter_records(model, db: AsyncSession, **filters):
    """Reusable function to filter records from a given model."""
    query = select(model).filter_by(**filters)
    result = await db.execute(query)
    return result.scalars().first()


def haversine(lat1, lon1, lat2, lon2):
    # Radius of Earth in meters
    R = 6371000

    # Convert latitude and longitude from degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in meters
    return R * c
