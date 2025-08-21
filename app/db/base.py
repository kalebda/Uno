import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base_class import Base


def is_running_in_docker():
    """Check if we're running inside a Docker container."""
    return os.path.exists("/.dockerenv")


def get_deployment_type():
    """Get the current deployment environment type."""
    return settings.DEPLOYMENT.lower()


def get_db_config():
    """Get database configuration based on deployment type and runtime environment."""
    deployment = get_deployment_type()
    in_docker = is_running_in_docker()

    config = {
        "user": settings.POSTGRES_USER,
        "password": settings.POSTGRES_PASSWORD,
        "port": settings.POSTGRES_PORT,
        "db_name": settings.POSTGRES_DB,
    }

    # Set host based on environment
    if in_docker:
        config["host"] = settings.POSTGRES_SERVER  # Should be "db" in docker-compose
    else:
        config["host"] = "localhost"

    if deployment != "local":
        config.update(
            {
                "region": os.getenv("AWS_REGION"),
                "secret_name": os.getenv("DB_PASSWORD_SECRET_NAME"),
            }
        )

    return config


def get_db_password(config):
    """Get database password based on deployment type."""
    deployment = get_deployment_type()
    if deployment == "local":
        return config["password"]

    try:
        if config.get("secret_name"):
            print("Getting password from AWS Secrets Manager")
            pass
        else:
            print("Getting password from IAM authentication")
            pass
    except Exception as e:
        print(f"Error getting AWS password: {str(e)}")
        if deployment in ["dev", "staging"]:
            return config["password"]
        raise


def get_sync_database_url():
    """Get synchronous database URL."""
    config = get_db_config()
    password = get_db_password(config)
    return f"postgresql://{config['user']}:{password}@{config['host']}:{config['port']}/{config['db_name']}"


def get_async_database_url():
    """Get asynchronous database URL."""
    config = get_db_config()
    password = get_db_password(config)
    return f"postgresql+asyncpg://{config['user']}:{password}@{config['host']}:{config['port']}/{config['db_name']}"


# Sync engine for migrations
engine = create_engine(
    get_sync_database_url(),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=900,
)

# Async engine for application
async_engine = create_async_engine(
    get_async_database_url(),
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Import all models to ensure they are registered with SQLAlchemy
import app.models  # noqa
