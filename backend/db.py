from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

DATABASE_URL = "sqlite+aiosqlite:///./database.db"

engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

DBSession = Annotated[AsyncSession, Depends(get_session)]

class Appartment(Base):
    __tablename__ = "appartments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    appartment_type: Mapped[str]
    num_rooms: Mapped[str]
    floor_area: Mapped[float]
    floor: Mapped[int]
    improvement: Mapped[str]
    address: Mapped[str]

async def create_tables() -> None:
    """Helpful function to create SQL tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
