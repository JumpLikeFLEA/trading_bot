import pandas as pd
import numpy as np
from typing import List, Dict
from src.strategies.base import StrategyBase, StrategyRegistry
from src.signals.models import Signal, SignalSide

@StrategyRegistry.register("ValueRankAlpha")
class ValueRankAlpha(StrategyBase):
    """
    Live Value-Based Alpha Strategy.
    Ranks tickers based on Yield and Inverse EV/EBITDA.
    """
    def __init__(self, name: str, buy_threshold: float = 0.8, sell_threshold: float = 0.5, tickers: List[str] = None, **kwargs):
        super().__init__(name, tickers=tickers, **kwargs)
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def generate_signals(self, market_data: Dict[str, pd.DataFrame], fundamental_data: pd.DataFrame = None) -> List[Signal]:
        """
        Generate signals based on fundamental ranking.
        
        Logic:
        1. Calculate Yield (operating_income / market_cap)
           - Using operatingCashflow as a proxy for operating income if not available.
        2. Calculate Inverse EV/EBITDA (1 / (enterprise_value / ebitda))
        3. Rank both metrics (pct=True) across all tickers.
        4. Generate BUY if avg rank > buy_threshold, SELL/EXIT if < sell_threshold.
        """
        if fundamental_data is None or fundamental_data.empty:
            return []

        df = fundamental_data.copy()

        # 1. Calculate Yield (operatingCashflow / marketCap)
        # Handle division by zero or NaN
        df['yield'] = df['operatingCashflow'] / df['marketCap']
        
        # 2. Calculate Inverse EV/EBITDA (ebitda / enterpriseValue)
        df['inv_ev_ebitda'] = df['ebitda'] / df['enterpriseValue']

        # Replace inf with NaN if any
        df.replace([np.inf, -np.inf], np.nan, inplace=True)

        # 3. Apply vectorized rank(pct=True)
        df['yield_rank'] = df['yield'].rank(pct=True)
        df['value_rank'] = df['inv_ev_ebitda'].rank(pct=True)

        # 4. Average Rank
        df['avg_rank'] = (df['yield_rank'] + df['value_rank']) / 2

        signals = []
        for ticker, row in df.iterrows():
            avg_rank = row['avg_rank']
            
            if pd.isna(avg_rank):
                continue

            if avg_rank > self.buy_threshold:
                side = SignalSide.BUY
            elif avg_rank < self.sell_threshold:
                side = SignalSide.SELL
            else:
                side = SignalSide.HOLD

            signals.append(Signal(
                symbol=ticker,
                side=side,
                strength=float(avg_rank), # Use rank as strength
                confidence=0.9,
                strategy_name=self.name,
                metadata={
                    "avg_rank": avg_rank,
                    "yield": row['yield'],
                    "inv_ev_ebitda": row['inv_ev_ebitda']
                }
            ))

        return signals
