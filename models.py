import datetime
import os
from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import (AsyncAttrs,async_sessionmaker, create_async_engine)

POSTGRES_USER = os.getenv("POSTGRES_USER", 'postgres')
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", '')
POSTGRES_DB = os.getenv("POSTGRES_DB", 'Aiohttp_dz')
POSTGRES_HOST = os.getenv("POSTGRES_HOST", '127.0.0.1')
POSTGRES_PORT = os.getenv("POSTGRES_PORT", '5431')

PG_DSN = (f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@'
          f'{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class Advertisement(Base):
    __tablename__ = 'advertisement'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    @property
    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": int(self.created_at.timestamp()),
        }


async def init_orm():
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()