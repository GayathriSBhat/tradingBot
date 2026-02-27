from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

ORDER_LOG = LOG_DIR / "orders.log"
DEBUG_LOG = LOG_DIR / "debug.log"


# --- Order Journal (1 line per order) ---
def log_order(symbol, side, order_type, quantity, price=None, status="SUCCESS", reason=None, balance=None):

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    line = f"{timestamp} | {symbol} | {side} | {order_type} | qty={quantity}"

    if order_type == "LIMIT":
        line += f" | price={price}"

    line += f" | {status}"

    if balance is not None:
        line += f" | bal={balance}"

    if status == "FAIL" and reason:
        line += f" | {reason.upper()}"

    with open(ORDER_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# --- Debug Diary (only when debug=True) ---
def log_debug(message, debug=False):
    if not debug:
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    with open(DEBUG_LOG, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {message}\n")


# --- Binance Error Interpreter ---
def interpret_binance_error(err, filters=None):

    code = err.get("code")
    msg = err.get("msg", "")

    if code == -2019:
        return "BALANCE", "Insufficient margin"

    elif code == -1013:
        if "notional" in msg.lower():
            min_notional = next(
                (
                    f.get("minNotional") or f.get("notional")
                    for f in (filters or [])
                    if f["filterType"] in ["NOTIONAL", "MIN_NOTIONAL"]
                ),
                "unknown"
            )
            return "NOTIONAL", f"Notional too low (min {min_notional} USDT)"

        if "price" in msg.lower():
            return "TICK", "Invalid price tick"

        return "INVALID", "Order rejected by filter"

    elif code == -1111:
        return "QTY", "Invalid quantity precision"

    elif code == -1100:
        return "INVALID", "Invalid input format"

    return "REJECT", "Exchange rejected order"