from __future__ import annotations
import os
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Float, JSON
import asyncio


DATABASE_URL = os.getenv("DATABASE_URL", "postgres://user:pass@db:5432/site").replace(
    "postgres://", "postgresql+asyncpg://"
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


class Site(Base):
    __tablename__ = "sites"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    host: Mapped[str] = mapped_column(String(255), unique=True)
    last_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    last_level: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))



class Vote(Base):
    __tablename__ = "votes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    host: Mapped[str] = mapped_column(String(255), index=True)
    user_id: Mapped[str] = mapped_column(String(255))
    label: Mapped[str] = mapped_column(String(32))
    reason: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))



async def init_db(max_retries: int = 30, delay: float = 1.0):
    last_err = None
    for _ in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return
        except Exception as e:
            last_err = e
            await asyncio.sleep(delay)
    # If still failing, raise last error to crash and surface logs
    raise last_err
