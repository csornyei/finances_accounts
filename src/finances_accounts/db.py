from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from finances_accounts.params import get_database_connection

DATABASE_URL = get_database_connection()

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency for route handlers
async def get_db():
    async with async_session() as session:
        yield session
