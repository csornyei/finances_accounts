import os

from finances_accounts.logger import logger


def get_database_connection() -> str:
    """
    Get the file handler type from environment variables.
    - POSTGRES_HOST=postgres
    - POSTGRES_PORT=5432
    - POSTGRES_USER=postgres
    - POSTGRES_PASSWORD=postgres

    """
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")

    if not db_host or not db_port or not db_user or not db_password or not db_name:
        logger.error(
            "Database connection parameters are not set in environment variables."
        )
        raise ValueError(
            "Database connection parameters are not set in environment variables."
        )

    return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
