from bot.client import BinanceClient

client = BinanceClient()

def place_market(symbol, side, quantity):
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity
    }
    return client.place_order(params)


def place_limit(symbol, side, quantity, price):
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "quantity": quantity,
        "price": price,
        "timeInForce": "GTC"
    }
    return client.place_order(params)