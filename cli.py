import typer
from typing import Optional

from bot.logging_config import setup_logging
from bot.validators import OrderInput
from bot.orders import place_market, place_limit

app = typer.Typer()

@app.command()
def place_order(
    symbol: str = typer.Option(..., help="Trading pair e.g. BTCUSDT"),
    side: str = typer.Option(..., help="BUY or SELL"),
    order_type: str = typer.Option(..., help="MARKET or LIMIT"),
    quantity: float = typer.Option(..., help="Order quantity"),
    price: Optional[float] = typer.Option(None, help="Price for LIMIT order"),
    debug: bool = typer.Option(False, help="Enable debug logging")
):
    setup_logging(debug=debug)

    try:
        order = OrderInput(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )

        print("\n=== Order Summary ===")
        print(order)

        if order.order_type == "MARKET":
            res = place_market(symbol, side, quantity)
        else:
            res = place_limit(symbol, side, quantity, price)

        print("\n=== Response ===")
        print(f"Order ID: {res.get('orderId')}")
        print(f"Status: {res.get('status')}")
        print(f"Executed Qty: {res.get('executedQty')}")
        print(f"Avg Price: {res.get('avgPrice')}")

        print("\nSUCCESS")

    except Exception as e:
        print("\nFAILED:", str(e))

if __name__ == "__main__":
    app()