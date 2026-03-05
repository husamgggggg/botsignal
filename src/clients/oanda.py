"""OANDA v20 REST API client."""
import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
import logging

from src.utils.retry import retry_with_backoff

logger = logging.getLogger(__name__)


class OANDAClient:
    """Client for OANDA v20 REST API."""
    
    def __init__(
        self,
        base_url: str,
        access_token: str,
        timeout: float = 30.0,
        max_retries: int = 5
    ):
        """Initialize OANDA client.
        
        Args:
            base_url: OANDA API base URL
            access_token: OANDA API access token
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an authenticated request to OANDA API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (e.g., "/v3/instruments/EUR_USD/candles")
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            httpx.HTTPStatusError: For HTTP errors
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        async def _make_request():
            response = await self._client.request(method, url, params=params)
            
            # Handle rate limiting (429)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "1")
                try:
                    wait_time = float(retry_after)
                except ValueError:
                    wait_time = 1.0
                
                logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
                
                # Retry once more after waiting
                response = await self._client.request(method, url, params=params)
            
            # Raise for other HTTP errors
            response.raise_for_status()
            return response.json()
        
        # Retry on 5xx errors and 429
        try:
            return await retry_with_backoff(
                _make_request,
                max_retries=self.max_retries,
                initial_delay=1.0,
                max_delay=60.0,
                retry_on=(httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException)
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise
    
    async def get_candles(
        self,
        instrument: str,
        granularity: str = "M5",
        count: int = 200,
        price: str = "M",
        smooth: bool = False,
        timezone: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch OHLC candles for an instrument.
        
        Args:
            instrument: Instrument pair (e.g., "EUR_USD")
            granularity: Timeframe (e.g., "M5", "M15", "H1")
            count: Number of candles to fetch
            price: Price component ("M" for mid, "B" for bid, "A" for ask)
            smooth: Whether to smooth the candles
            timezone: Optional timezone (e.g., "America/New_York")
            
        Returns:
            List of completed candles (only candles with complete=True)
            Each candle dict contains: time, open, high, low, close, volume, complete
        """
        endpoint = f"/v3/instruments/{instrument}/candles"
        
        params = {
            "granularity": granularity,
            "count": count,
            "price": price
        }
        
        if smooth:
            params["smooth"] = "true"
        if timezone:
            params["time"] = timezone
        
        try:
            logger.debug(f"Fetching {count} candles for {instrument} ({granularity})")
            response = await self._request("GET", endpoint, params=params)
            
            candles = response.get("candles", [])
            
            # Filter to only completed candles
            completed_candles = [
                {
                    "time": candle.get("time"),
                    "open": float(candle["mid"]["o"]),
                    "high": float(candle["mid"]["h"]),
                    "low": float(candle["mid"]["l"]),
                    "close": float(candle["mid"]["c"]),
                    "volume": int(candle.get("volume", 0)),
                    "complete": candle.get("complete", True)
                }
                for candle in candles
                if candle.get("complete", True) and "mid" in candle
            ]
            
            logger.info(
                f"Retrieved {len(completed_candles)} completed candles for {instrument} "
                f"(requested {count}, total in response: {len(candles)})"
            )
            
            return completed_candles
            
        except Exception as e:
            logger.error(f"Failed to fetch candles for {instrument}: {e}")
            raise

