from pydantic import BaseModel
from typing import Optional, List

class FarmerBase(BaseModel):
    name: str
    phone: str
    village: str
    district: str
    crops: Optional[str]
    land_size: Optional[float]

class FarmerResponse(FarmerBase):
    farmer_id: int

    class Config:
        orm_mode = True

class FarmerWithPayments(FarmerResponse):
    payments: List[dict] = []