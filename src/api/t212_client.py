import logging
import requests
import pandas as pd
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

# --- Logging Setup ---
# Setup logger for the API module
logger = logging.getLogger("trading_bot.api")
logger.setLevel(logging.INFO)

# --- Exceptions ---
class T212Error(Exception):
    """Custom exception for Trading 212 API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

# --- Models ---
class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class AccountCash(BaseModel):
    free: float
    total: float
    used: float
    ppl: float

class Position(BaseModel):
    ticker: str
    quantity: float
    average_price: float = Field(..., alias="averagePrice")
    current_price: float = Field(..., alias="currentPrice")
    ppl: float

class Instrument(BaseModel):
    ticker: str
    name: str
    isin: str
    currency_code: str = Field(..., alias="currencyCode")

# --- Client ---
class T212Client:
    """
    High-level wrapper for the Trading 212 REST API.
    Operates on Practice Mode by default.
    """
    BASE_URL = "https://demo.trading212.com/api/v0"

    def __init__(self, api_key: str, dry_run: bool = False):
        self.api_key = api_key
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.headers.update({"Authorization": self.api_key})

    def _request(self, method: str, endpoint: str, params: Dict[str, Any] = None, json: Dict[str, Any] = None) -> Any:
        """
        Generic request handler with error management for 429 and 503.
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        if self.dry_run and method in ["POST", "PUT", "DELETE"]:
            logger.info(f"[DRY RUN] {method} request to {url} with data: {json or params}")
            return {"status": "DRY_RUN_SUCCESS", "orderId": "DRY_RUN_ID"}

        try:
            response = self.session.request(method, url, params=params, json=json)
            
            if response.status_code == 429:
                logger.warning("Rate limit hit (429). Waiting or failing.")
                raise T212Error("Rate limit exceeded", status_code=429)
            elif response.status_code == 503:
                logger.warning("Service under maintenance (503).")
                raise T212Error("Service unavailable / Maintenance", status_code=503)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"API Request failed: {e}"
            logger.error(error_msg)
            status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            raise T212Error(error_msg, status_code=status_code)

    def get_account_cash(self) -> AccountCash:
        """Fetch account cash details."""
        data = self._request("GET", "/equity/account/cash")
        return AccountCash(**data)

    def get_open_positions(self) -> List[Position]:
        """Fetch current open positions."""
        data = self._request("GET", "/equity/portfolio")
        return [Position(**p) for p in data]

    def get_instruments(self) -> List[Instrument]:
        """Fetch all available instruments."""
        data = self._request("GET", "/equity/metadata/instruments")
        return [Instrument(**i) for i in data]

    def place_order(self, ticker: str, quantity: float, order_type: OrderType = OrderType.MARKET, limit_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Place an order.
        quantity: positive for Buy, negative for Sell.
        """
        is_buy = quantity > 0
        abs_quantity = abs(quantity)
        
        payload = {
            "ticker": ticker,
            "quantity": abs_quantity,
            "action": "BUY" if is_buy else "SELL"
        }
        
        if order_type == OrderType.MARKET:
            endpoint = "/equity/orders/market"
        elif order_type == OrderType.LIMIT:
            if limit_price is None:
                raise ValueError("limit_price is required for LIMIT orders")
            endpoint = "/equity/orders/limit"
            payload["limitPrice"] = limit_price
        else:
            raise NotImplementedError(f"Order type {order_type} not yet implemented in this shell.")

        logger.info(f"Placing {order_type.value} {payload['action']} order for {ticker}: quantity={abs_quantity}")
        
        return self._request("POST", endpoint, json=payload)
