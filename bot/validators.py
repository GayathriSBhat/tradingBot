from pydantic import BaseModel, validator
from decimal import Decimal

from bot.client import BinanceClient
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

    def validate_symbol(self,symbol):
        client=BinanceClient()
        client.get_symbol_filters(symbol)

    def validate_order(self, symbol, price, quantity, filters):
        errors = []

        price_dec = Decimal(str(price)) if price else None
        qty_dec = Decimal(str(quantity))

        min_notional = None

        for f in filters:

            # ----- LOT SIZE -----
            if f["filterType"] == "LOT_SIZE":
                min_qty = Decimal(f["minQty"])
                step_size = Decimal(f["stepSize"])

                if qty_dec < min_qty:
                    errors.append(f"Quantity must be ≥ {min_qty}")

                if qty_dec % step_size != 0:
                    errors.append(f"Quantity must follow step size {step_size}")

            # ----- PRICE FILTER (tick size) -----
            elif f["filterType"] == "PRICE_FILTER":
                tick = Decimal(f["tickSize"])

                if price_dec and price_dec % tick != 0:
                    errors.append(f"Price must be multiple of tick size {tick}")

            # ----- NOTIONAL -----
            elif f["filterType"] in ["NOTIONAL", "MIN_NOTIONAL"]:
                min_notional = Decimal(
                    f.get("notional") or f.get("minNotional")
                )

        # Check notional after loop
        if price_dec and min_notional:
            notional = price_dec * qty_dec

            if notional < min_notional:
                errors.append(
                    f"Order value {notional} < minimum {min_notional}"
                )

        return errors