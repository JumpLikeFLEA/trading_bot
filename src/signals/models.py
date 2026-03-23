from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime

class SignalSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class Signal(BaseModel):
    """
    Normalized signal object produced by Alpha strategies.
    """
    symbol: str = Field(..., description="Ticker symbol (e.g., 'AAPL_US_EQ')")
    side: SignalSide = Field(..., description="Trading side (BUY, SELL, HOLD)")
    strength: float = Field(default=1.0, ge=0.0, le=1.0, description="Normalized signal strength (0 to 1)")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score (0 to 1)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Signal generation timestamp")
    strategy_name: str = Field(..., description="Name of the strategy that generated the signal")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional strategy-specific data")

    class Config:
        use_enum_values = True
