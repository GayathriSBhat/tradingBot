import os
import time
import hmac
import hashlib
import httpx
import logging
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")

API_SECRET = os.getenv("BINANCE_API_SECRET")

BASE_URL = os.getenv("BASE_URL")

class BinanceClient:

    def _sign(self, params):
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            API_SECRET.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def place_order(self, params):
        params["timestamp"] = int(time.time() * 1000)
        params["signature"] = self._sign(params)

        headers = {"X-MBX-APIKEY": API_KEY}

        url = f"{BASE_URL}/fapi/v1/order"

        try:
            response = httpx.post(url, params=params, headers=headers)
            logging.info(f"Request: {params}")
            logging.info(f"Response: {response.text}")
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logging.error(f"API error: {e}")
            raise

    def get_mark_price(self, symbol: str):
        url = f"{BASE_URL}/fapi/v1/premiumIndex"

        params = {"symbol": symbol}

        response = httpx.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        return float(data["markPrice"])

    def get_symbol_filters(self,symbol):
        url = f"{BASE_URL}/fapi/v1/exchangeInfo"
        res = httpx.get(url).json()

        for s in res["symbols"]:
            if s["symbol"] == symbol:
                return s["filters"]

        raise ValueError("Symbol not found")

    def get_symbols(self):
        url = f"{BASE_URL}/fapi/v1/exchangeInfo"

        response = httpx.get(url)
        response.raise_for_status()

        data = response.json()

        symbols = []

        for s in data["symbols"]:
            if s["status"] == "TRADING":  # only active symbols
                symbols.append(s["symbol"])

        return symbols

    