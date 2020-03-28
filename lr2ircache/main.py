from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/items/{bmsmd5}", response_model=schemas.Item)
def read_item(bmsmd5: str, db: Session = Depends(get_db)):
    try:
        db_item = crud.get_item(db, bmsmd5)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if db_item is None:
        raise HTTPException(status_code=404, detail="item not found")

    return db_item
