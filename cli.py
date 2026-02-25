import typer
from typing import Optional
from bot.logging_config import setup_logging
from bot.validators import OrderInput
from bot.client import BinanceClient
from bot.orders import place_market, place_limit
from rich.console import Console
from rich.table import Table


app = typer.Typer()
console = Console()

# to extract tick rate, stock qty from market before user can place an order(to make informed decisions)
def summarize_filters(filters):
    min_qty = None
    tick = None
    min_notional = None

    for f in filters:
        if f["filterType"] == "LOT_SIZE":
            min_qty = f["minQty"]

        if f["filterType"] == "PRICE_FILTER":
            tick = f["tickSize"]

        if f["filterType"] in ["NOTIONAL", "MIN_NOTIONAL"]:
            min_notional = f.get("notional") or f.get("minNotional")

    print("\nTrading constraints:")
    print(f"Min quantity: {min_qty}")
    print(f"Tick size: {tick}")
    print(f"Min notional: {min_notional}")

# interactive cli
def interactive(debug: bool = False):
    client = BinanceClient()

    # Show available symbols -bitcoins (trading contract)
    items=client.get_symbols()
    table = Table(title="Available Symbols")
    table.add_column("Symbol")

    for item in items:
        table.add_row(item)

    console.print(table)

    # step 1- enter symbol 
    symbol = typer.prompt("Symbol", default="BTCUSDT")

    # Step 2 — show market price & filters {filters:stock qty available, tick size, etc}
    
    mark_price = client.get_mark_price(symbol)
    filters = client.get_symbol_filters(symbol)
    print("\n=== Market Snapshot ===")
    print(f"{symbol} mark price: {mark_price}")
    summarize_filters(filters)

    # Step 3 — confirmation
    if not typer.confirm("Do you want to place an order?"):
        print("Exiting.")
        raise typer.Exit()

    # Step 4 — ask inputs    
    side = typer.prompt("Side (BUY/SELL)")
    reduceOnly = False
    if side=='SELL':
        reduceOnly=typer.prompt("Reduce only?False/True:")
    order_type = typer.prompt("Order type (MARKET/LIMIT)")    
    price = None
    if order_type == "LIMIT":
        price = float(typer.prompt("Price"))
    quantity = float(typer.prompt("Quantity"))

    # Step 5 — validation (pydantic - important to verify query before sending API requests)
    order = OrderInput(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
    )
    
    errors = order.validate_order(symbol, price, quantity, filters) 
    if errors:
        print("Order validation failed:")
        for e in errors:
            print("-", e)
        return

    print("\n=== Order Summary ===")
    print(order)  
    print("\n=== debug info ===")

    #Step 6 Place order and catch errors while sending API request
    try:
        setup_logging(debug=debug)
        if order.order_type == "MARKET":
            res = place_market(symbol, side, quantity, reduceOnly)
        else:
            res = place_limit(symbol, side, quantity, price, reduceOnly)
    except Exception as e:
        print("\nFAILED:", str(e))
        return

    # Print if order was placed
    print("\n=== Response ===")
    print(f"Order ID: {res.get('orderId')}")
    print(f"Status: {res.get('status')}")
    print(f"Executed Qty: {res.get('executedQty')}")
    print(f"Avg Price: {res.get('avgPrice')}")

    print("\nSUCCESS")



# used to make entrypoint interactive
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, debug: bool = typer.Option(False, help="Enable debug mode")):
    if ctx.invoked_subcommand is None:
        interactive(debug=debug)
      
if __name__ == "__main__":
    app()