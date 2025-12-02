import asyncio
from enum import Enum

import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from db import Appartment, DBSession, create_tables
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, ...)
    allow_headers=["*"],  # Разрешить любые хедеры
)

class AppartmentEnum(Enum):
    APPARTMENT = "appartment"
    HOUSE = "house"

class WriteSingleAppartmentData(BaseModel):
    appartment_type: AppartmentEnum
    num_rooms: int
    floor_area: float
    floor: int
    improvement: str
    address: str

class ReadSingleAppartmentData(WriteSingleAppartmentData):
    id: int

    model_config = ConfigDict(from_attributes=True)
@app.post(
    "/",
    response_model=ReadSingleAppartmentData
)
async def create(appartment_data: WriteSingleAppartmentData, db_sess: DBSession):

    new_appartment = Appartment(
        appartment_type=appartment_data.appartment_type.value,
        num_rooms=appartment_data.num_rooms,
        floor_area=appartment_data.floor_area,
        floor=appartment_data.floor,
        improvement=appartment_data.improvement,
        address=appartment_data.address,
    )

    db_sess.add(new_appartment)
    await db_sess.commit()

    return new_appartment

@app.get(
    "/",
    response_model=list[ReadSingleAppartmentData]
)
async def get_list(
        db_sess: DBSession,
        num_rooms: int | None = Query(None),
        floor_area: float | None = Query(None),
        floor: int | None = Query(None),
        appartment_type: str | AppartmentEnum = Query(None)
):
    query = select(Appartment)

    if num_rooms:
        query = query.where(Appartment.num_rooms == num_rooms)
    if floor_area:
        query = query.where(Appartment.floor_area == floor_area)
    if floor:
        query = query.where(Appartment.floor == floor)
    if appartment_type:
        query = query.where(Appartment.appartment_type == appartment_type)

    res = await db_sess.execute(query)
    res = res.scalars().all()


    return [ReadSingleAppartmentData.model_validate(row) for row in res]

@app.delete(
    "/{appartment_id}",
    status_code=204,
)
async def delete(
        db_sess: DBSession,
        appartment_id: int
):
    obj = await db_sess.get(Appartment, appartment_id)

    await db_sess.delete(obj)
    await db_sess.commit()
    return

if __name__ == '__main__':
    asyncio.run(create_tables())
    uvicorn.run(app, host="0.0.0.0", port=8008)