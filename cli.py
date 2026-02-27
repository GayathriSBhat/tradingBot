import typer
from bot.validators import OrderInput
from bot.client import BinanceClient
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

def get_constraints_summary(filters):
    """Summarizes exchange rules for the user."""
    summary = {"min_qty": 0.0, "step_size": 0.0, "tick_size": 0.0, "min_notional": 0.0}
    for f in filters:
        if f["filterType"] == "LOT_SIZE":
            summary["min_qty"] = f["minQty"]
            summary["step_size"] = f["stepSize"]
        elif f["filterType"] == "PRICE_FILTER":
            summary["tick_size"] = f["tickSize"]
        elif f["filterType"] in ["NOTIONAL", "MIN_NOTIONAL"]:
            summary["min_notional"] = f.get("notional") or f.get("minNotional")
    
    console.print("\n[bold yellow]Trading Constraints:[/bold yellow]")
    console.print(f"Min Qty: {summary['min_qty']} | Step: {summary['step_size']}")
    console.print(f"Tick: {summary['tick_size']} | Min Notional: {summary['min_notional']}")
    return summary

def get_testnet_dashboard_url(symbol: str):
    return f"https://testnet.binancefuture.com/en/futures/{symbol}"

def interactive():
    client = BinanceClient()

    # Show available balance, assets
    def show_balance():
        account_info = client.get_account_info()

        console.print("\n[bold cyan]ACCOUNT SUMMARY[/bold cyan]")
        console.print("="*60)

        console.print(f"Available Balance: {account_info['availableBalance']} USDT")
        console.print(f"Total Wallet Balance: {account_info['totalWalletBalance']} USDT")
        console.print(f"Unrealized PnL: {account_info['totalUnrealizedProfit']} USDT")

        console.print("\n[bold]Assets:[/bold]")

        for asset in account_info.get("assets", []):
            wallet = float(asset.get("walletBalance", 0))
            pnl = float(asset.get("unrealizedProfit", 0))
            
            if wallet != 0 or pnl != 0:
                console.print(
                    f"{asset['asset']} | Wallet: {wallet} | Unrealized PnL: {pnl}"
                )

        console.print("="*60)
    
    show_balance()

    # 1. Symbol Selection
    symbols = client.get_symbols()
    table = Table(title="Live Trading Symbols")
    table.add_column("Symbol", style="cyan")
    for s in symbols[:15]: 
        table.add_row(s)
    console.print(table)

    symbol = typer.prompt("Symbol", default="BTCUSDT").upper()
    
    # 2. Market Snapshot
    mark_price = client.get_mark_price(symbol)
    filters = client.get_symbol_filters(symbol)
    summary_data = get_constraints_summary(filters)

    console.print(f"\n[green]Mark Price: {mark_price}[/green]")
    if not typer.confirm("Open order inputs?"): return

    # 3. Inputs
    side = typer.prompt("Side (BUY/SELL)").upper()
    reduce_only = typer.confirm("Reduce Only?") if side == "SELL" else False
    order_type = typer.prompt("Type (MARKET/LIMIT)").upper()

    price = None
    if order_type == "LIMIT":
        price = float(typer.prompt("Price"))
    quantity = float(typer.prompt("Quantity"))

    # 4. Local Validation
    try:
        order = OrderInput(symbol=symbol, side=side, order_type=order_type, quantity=quantity, price=price)
        order.normalize_quantities(filters)
        
        # Margin Check
        balance, leverage = client.get_balance_and_leverage(symbol)
        check_price = order.price if order.price else mark_price
        cost = (order.quantity * check_price) / leverage
        
        if cost > balance:
            console.print(f"\n[red]INSUFFICIENT MARGIN: Need {cost:.2f} USDT, Have {balance:.2f} USDT[/red]")
            return

        errors = order.validate_against_filters(filters, mark_price)
        if errors:
            for e in errors: console.print(f"[red]- {e}[/red]")
            return

        # 5. API Execution

        payload = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": order.quantity,
            "reduceOnly": reduce_only
        }

        if order.order_type == "LIMIT":
            payload["price"] = order.price
            payload["timeInForce"] = "GTC" # Mandatory for Limit orders

        res = client.place_order(payload)
        console.print(f"\n[bold green]SUCCESS! Order ID: {res['orderId']}[/bold green]")
        dashboard_url = get_testnet_dashboard_url(symbol)
        console.print(f"[cyan]Verify on Binance Testnet Dashboard:[/cyan] {dashboard_url}")

    except Exception as e:
        console.print(f"\n[bold red]TRADE FAILED: {e}[/bold red]")
        dashboard_url = get_testnet_dashboard_url(symbol)
        console.print(f"[yellow]Check on Testnet Dashboard:[/yellow] {dashboard_url}")

    show_balance()

if __name__ == "__main__":
    interactive()