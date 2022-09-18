from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

import models
from database import SessionLocal, engine



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


models.Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Address(BaseModel):
    state: str = Field(min_length=1)
    city: str = Field(min_length=1)
    zip_code: int = Field(gt=-1)
    street: str = Field(min_length=1)
    longitude: float = Field(gt=-1)
    latitude: float = Field(gt=-1)


class AddressUpdate(BaseModel):
    state: Optional[str] = Field(min_length=1)
    city: Optional[str] = Field(min_length=1)
    zip_code: Optional[int] = Field(gt=-1)
    street: Optional[str] = Field(min_length=1)
    longitude: Optional[float] = Field(gt=-1)
    latitude: Optional[float] = Field(gt=-1)


@app.get("/adresses")
def fetch(longitude: Optional[int] = None, latitude: Optional[int] = None,db: Session = Depends(get_db)):
    # If longitude and latitude is given return addresses within coordinates
    if longitude and latitude:
        addresses = db.query(models.Address).filter(
            models.Address.longitude <= longitude,
            models.Address.latitude <= latitude).all()
    else:
        addresses = db.query(models.Address).all()
    return addresses


@app.get("/adresses/{address_id}")
def fetch(address_id: int ,db: Session = Depends(get_db)):
    address = db.query(models.Address).get(address_id)
    if not address:
        raise HTTPException(status_code=404, detail=f"Address with the id {id} does not exists")
    return address


@app.post("/adresses")
def add(payload:Address, db: Session = Depends(get_db), status_code=status.HTTP_201_CREATED):
    new_address = models.Address(
        state = payload.state,
        city = payload.city,
        zip_code = payload.zip_code,
        street = payload.street,
        longitude = payload.longitude,
        latitude = payload.latitude
    )
    db.add(new_address)
    db.commit()
    return 'Address Created Successfully'


@app.put("/adresses/{address_id}")
def update(id:int, payload:AddressUpdate, db: Session = Depends(get_db)):
    address = db.query(models.Address).get(id)
    if not address:
        raise HTTPException(status_code=404, detail=f"Address with the id {id} does not exists")
    address_data = payload.dict(exclude_unset=True)
    for key, value in address_data.items():
        setattr(address, key, value)
    db.add(address)
    db.commit()
    db.refresh(address)
    return "Address Update Successfully"


@app.delete("/address/{address_id}")
def delete(id:int, db: Session = Depends(get_db)):
    address = db.query(models.Address).get(id)
    if not address:
        raise HTTPException(status_code=404, detail=f"Address with the id {id} does not exists")
    db.delete(address)
    db.commit()
    return 'Address Deleted Successfully'