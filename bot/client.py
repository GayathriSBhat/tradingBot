import os, time, hmac, hashlib, httpx, urllib.parse, logging
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
# Base URL (Mainnet: https://fapi.binance.com | Testnet: https://testnet.binancefuture.com)
BASE_URL = os.getenv("BASE_URL", "https://fapi.binance.com")

logger = logging.getLogger("tradebot")


class BinanceClient:
    def __init__(self):
        self.headers = {"X-MBX-APIKEY": API_KEY} if API_KEY else {}

    def _sign(self, query_string: str) -> str:
        """Generates HMAC SHA256 signature using the API Secret."""
        return hmac.new(
            API_SECRET.encode('utf-8'), 
            query_string.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()

    def _handle_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Centralized handler for all API requests with rate limit tracking."""
        try:
            with httpx.Client(timeout=10.0) as client:
                # Log the outgoing request (debug level to avoid noisy console output)
                logger.debug(f"HTTP Request: {method} {url}")
                response = client.request(method, url, **kwargs)

                # Monitor Rate Limits
                weight = response.headers.get("X-MBX-USED-WEIGHT-1M")
                if weight:
                    logger.debug(f"[Rate Limit] IP Weight: {weight}/2400")

                # Log request params and response summary
                try:
                    params_or_data = kwargs.get("params") or kwargs.get("data") or {}
                    logger.debug(f"Request: {params_or_data}")
                except Exception:
                    pass

                try:
                    # attempt to log JSON response when possible, fallback to text
                    body = response.json()
                except Exception:
                    body = response.text
                logger.debug(f"Response: {body}")

                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise Exception(f"Rate Limit Hit! Retry after {e.response.headers.get('Retry-After')}s")
            try:
                error_data = e.response.json()
                # log exchange error details at DEBUG
                logger.debug("Exchange error response: %s", error_data)
                raise Exception(f"Exchange Error {error_data.get('code')}: {error_data.get('msg')}")
            except:
                raise Exception(f"HTTP Error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Network Error: {str(e)}")

    def get_symbols(self) -> List[str]:
        """Returns all symbols currently available for trading."""
        data = self._handle_request("GET", f"{BASE_URL}/fapi/v1/exchangeInfo")
        return [s["symbol"] for s in data.get("symbols", []) if s["status"] == "TRADING"]

    def get_mark_price(self, symbol: str) -> float:
        """Fetches the current Mark Price for a specific symbol."""
        data = self._handle_request("GET", f"{BASE_URL}/fapi/v1/premiumIndex", params={"symbol": symbol.upper()})
        return float(data.get("markPrice", 0.0))

    def get_symbol_filters(self, symbol: str) -> List[Dict]:
        """Fetches trading rules/constraints for the symbol."""
        data = self._handle_request("GET", f"{BASE_URL}/fapi/v1/exchangeInfo")
        for s in data["symbols"]:
            if s["symbol"] == symbol.upper():
                return s["filters"]
        raise ValueError(f"Symbol {symbol} not found.")

    def get_balance_and_leverage(self, symbol: str):
        """Fetches account balance and leverage for margin validation."""
        ts = int(time.time() * 1000)
        query = f"timestamp={ts}&recvWindow=5000"
        signature = self._sign(query)
        url = f"{BASE_URL}/fapi/v2/account?{query}&signature={signature}"
        
        data = self._handle_request("GET", url, headers=self.headers)
        balance = next((float(a["availableBalance"]) for a in data["assets"] if a["asset"] == "USDT"), 0.0)
        leverage = next((int(p["leverage"]) for p in data["positions"] if p["symbol"] == symbol.upper()), 20)
        return balance, leverage

    def get_position_amount(self, symbol: str) -> float:
        """Return the current position amount for the given symbol.

        Positive value indicates a long position, negative indicates a short
        position, and 0.0 means no open position.
        """
        ts = int(time.time() * 1000)
        query = f"timestamp={ts}&recvWindow=5000"
        signature = self._sign(query)
        url = f"{BASE_URL}/fapi/v2/account?{query}&signature={signature}"

        data = self._handle_request("GET", url, headers=self.headers)
        pos = next((p for p in data.get("positions", []) if p.get("symbol") == symbol.upper()), None)
        if not pos:
            return 0.0
        try:
            return float(pos.get("positionAmt", 0.0))
        except Exception:
            return 0.0

    def place_order(self, params: Dict):
        """Signs and executes a new order on Binance."""
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = 5000
        
        # Ensure booleans are 'true'/'false' strings
        for k, v in params.items():
            if isinstance(v, bool):
                params[k] = str(v).lower()
        
        query_string = urllib.parse.urlencode(params)
        signature = self._sign(query_string)
        url = f"{BASE_URL}/fapi/v1/order?{query_string}&signature={signature}"
        
        return self._handle_request("POST", url, headers=self.headers)