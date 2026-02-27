import typer
import logging
from bot.validators import OrderInput
from bot.client import BinanceClient
from rich.console import Console
from rich.table import Table
from bot.logging_config import (log_order, log_debug, interpret_binance_error)

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

def debug_print(console, message, debug):
    if not debug:
        return
    from rich.table import Table

    table = Table(show_header=False)
    table.add_column("Type", style="cyan", width=12)
    table.add_column("Details", style="white")

    table.add_row("DEBUG", message)
    console.print(table)

    log_debug(message, debug)

def interactive(debug: bool = False):
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
        while True:
            price = float(typer.prompt("Price"))
            if price <= 0:
                console.print("[red]Please enter a positive value[/red]")
            else:
                break
    while True:
        quantity = float(typer.prompt("Quantity"))
        if quantity <= 0:
            console.print("[red]Please enter a positive value[/red]")
        else:
            break

    # 4. Local Validation
    debug_msg = None
    reason = None
    try:
        order = OrderInput(symbol=symbol, side=side, order_type=order_type, quantity=quantity, price=price)
        order.normalize_quantities(filters)
        
        # Margin Check
        balance, leverage = client.get_balance_and_leverage(symbol) 
        check_price = order.price if order.price else mark_price
        notional = order.quantity * check_price
        required_margin = notional / leverage

        if not reduce_only and required_margin > balance:
            console.print(
                f"\n[red]INSUFFICIENT MARGIN: Need {required_margin:.2f} USDT, Have {balance:.2f} USDT[/red]"
            )
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
        
        account_info = client.get_account_info()
        balance = account_info['availableBalance']

        console.print(f"\n[bold green]SUCCESS! Order ID: {res['orderId']}[/bold green]")
        log_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=order.quantity,
            price=order.price,
            status="SUCCESS"
        )
         
        dashboard_url = get_testnet_dashboard_url(symbol)
        console.print(f"[cyan]Verify on Binance Testnet Dashboard:[/cyan] {dashboard_url}")

    except Exception as e:
        reason = "REJECT"
        debug_msg = "Unknown error"

        if isinstance(e.args[0], dict):
            reason, debug_msg = interpret_binance_error(e.args[0], filters)

        console.print(f"\n[bold red]ORDER FAILED: {reason}[/bold red]")

        try:
            account_info = client.get_account_info()
            balance = account_info['availableBalance']
        except:
            balance = "unknown"

        log_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            status="FAIL",
            reason=reason,
            balance=balance
        )

        debug_print(console, debug_msg, debug)

    dashboard_url = get_testnet_dashboard_url(symbol)
    console.print(f"[yellow]Check on Testnet Dashboard:[/yellow] {dashboard_url}")

    show_balance()

if __name__ == "__main__":
    interactive(debug=False)