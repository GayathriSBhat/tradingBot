from pydantic import BaseModel, validator

class OrderInput(BaseModel):
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float | None = None

    @validator("side")
    def validate_side(cls, v):
        if v not in ["BUY", "SELL"]:
            raise ValueError("Side must be BUY or SELL")
        return v

    @validator("order_type")
    def validate_type(cls, v):
        if v not in ["MARKET", "LIMIT"]:
            raise ValueError("Order type must be MARKET or LIMIT")
        return v

    @validator("price", always=True)
    def validate_price(cls, v, values):
        if values.get("order_type") == "LIMIT" and v is None:
            raise ValueError("Price required for LIMIT order")
        return v