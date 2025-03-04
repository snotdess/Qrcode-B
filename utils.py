#### app/utils.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def filter_records(model, db: AsyncSession, **filters):
    """Reusable function to filter records from a given model."""
    query = select(model).filter_by(**filters)
    result = await db.execute(query)
    return result.scalars().first()
