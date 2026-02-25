from bot.client import BinanceClient

client = BinanceClient()

def place_market(symbol, side, quantity, reduceOnly):
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "reduceOnly": reduceOnly
    }
    return client.place_order(params)


def place_limit(symbol, side, quantity, price, reduceOnly):
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "quantity": quantity,
        "price": price,
        "reduceOnly": reduceOnly,
        "timeInForce": "GTC"
    }
    return client.place_order(params)