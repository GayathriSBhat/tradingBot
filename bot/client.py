import os
import time
import hmac
import hashlib
import httpx
import logging
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
print("API KEY:", API_KEY[:6])
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