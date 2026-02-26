from pydantic import BaseModel, field_validator, model_validator
from decimal import Decimal, ROUND_DOWN

class OrderInput(BaseModel):
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float | None = None

    @field_validator("side")
    @classmethod
    def validate_side(cls, v):
        if v.upper() not in ["BUY", "SELL"]:
            raise ValueError("Side must be BUY or SELL")
        return v.upper()

    @field_validator("order_type")
    @classmethod
    def validate_type(cls, v):
        if v.upper() not in ["MARKET", "LIMIT"]:
            raise ValueError("Order type must be MARKET or LIMIT")
        return v.upper()

    @model_validator(mode='after')
    def validate_price_requirement(self) -> 'OrderInput':
        if self.order_type == "LIMIT" and self.price is None:
            raise ValueError("Price is required for LIMIT orders")
        return self

    def normalize_quantities(self, filters: list):
        """
        Automatically rounds price/qty to match exchange stepSize and tickSize.
        Updates the object's quantity and price in-place.
        """
        for f in filters:
            if f["filterType"] == "LOT_SIZE":
                step = Decimal(f["stepSize"])
                # Quantize rounds to the exact decimal places allowed by the step
                self.quantity = float(Decimal(str(self.quantity)).quantize(step, rounding=ROUND_DOWN))
            
            if f["filterType"] == "PRICE_FILTER" and self.price:
                tick = Decimal(f["tickSize"])
                self.price = float(Decimal(str(self.price)).quantize(tick, rounding=ROUND_DOWN))

    def validate_against_filters(self, filters: list, current_market_price: float = None):
        """
        Validates the order against exchange filters.
        """
        errors = []
        qty_dec = Decimal(str(self.quantity))
        
        # Determine price to use for Notional check
        price_to_check = self.price if self.price else current_market_price
        if not price_to_check:
            return ["Cannot validate: Market price unknown."]
            
        check_price = Decimal(str(price_to_check))
        
        for f in filters:
            f_type = f["filterType"]

            if f_type == "LOT_SIZE":
                min_qty = Decimal(f["minQty"])
                max_qty = Decimal(f["maxQty"])
                step_size = Decimal(f["stepSize"])

                if qty_dec < min_qty:
                    errors.append(f"Quantity {qty_dec} below min {min_qty}")
                if qty_dec > max_qty:
                    errors.append(f"Quantity {qty_dec} above max {max_qty}")
                # Check if quantity is a valid multiple of step size
                if qty_dec % step_size != 0:
                    errors.append(f"Quantity {qty_dec} must follow step size {step_size}")

            elif f_type == "PRICE_FILTER" and self.price:
                tick = Decimal(f["tickSize"])
                if check_price % tick != 0:
                    errors.append(f"Price {check_price} must follow tick size {tick}")

            elif f_type in ["NOTIONAL", "MIN_NOTIONAL"]:
                min_notional = Decimal(f.get("notional") or f.get("minNotional"))
                notional = qty_dec * check_price
                if notional < min_notional:
                    errors.append(f"Notional {notional} below min {min_notional}")

        return errors