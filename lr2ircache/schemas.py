from pydantic import BaseModel


class Item(BaseModel):
    type: str
    lr2_id: int
    bmsmd5: str
    title: str

    class Config:
        orm_mode = True
