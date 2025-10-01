"""
MACD Strategy

MACD (Moving Average Convergence Divergence) 지표를 사용한 전략입니다.
MACD선과 시그널선의 교차를 이용하여 매매 신호를 생성합니다.
"""

import pandas as pd
from .base import TradingStrategy


class MACDStrategy(TradingStrategy):
    """
    MACD 전략

    MACD선(단기EMA - 장기EMA)과 시그널선(MACD의 이동평균)의
    교차를 이용하여 매매 신호를 생성합니다.

    매수 신호: MACD선 > 시그널선 (상향 돌파)
    매도 신호: MACD선 < 시그널선 (하향 돌파)
    """

    def __init__(self, params: dict):
        """
        MACD 전략 초기화

        Args:
            params (dict): 전략 파라미터
                - fast_period (int): 단기 EMA 기간 (기본: 12)
                - slow_period (int): 장기 EMA 기간 (기본: 26)
                - signal_period (int): 시그널선 기간 (기본: 9)

        Example:
            strategy = MACDStrategy({
                'fast_period': 12,
                'slow_period': 26,
                'signal_period': 9
            })
        """
        super().__init__(params)
        self.fast_period = params.get('fast_period', 12)
        self.slow_period = params.get('slow_period', 26)
        self.signal_period = params.get('signal_period', 9)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        MACD 지표를 계산합니다.

        MACD 계산:
        1. 단기 EMA (기본 12일)
        2. 장기 EMA (기본 26일)
        3. MACD선 = 단기 EMA - 장기 EMA
        4. 시그널선 = MACD선의 EMA (기본 9일)
        5. 히스토그램 = MACD선 - 시그널선

        Args:
            data (pd.DataFrame): OHLCV 데이터

        Returns:
            pd.DataFrame: MACD 지표가 추가된 데이터
                - macd: MACD선
                - macd_signal: 시그널선
                - macd_histogram: 히스토그램
        """
        # 단기/장기 EMA 계산
        ema_fast = data['close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = data['close'].ewm(span=self.slow_period, adjust=False).mean()

        # MACD선 = 단기 EMA - 장기 EMA
        data['macd'] = ema_fast - ema_slow

        # 시그널선 = MACD선의 EMA
        data['macd_signal'] = data['macd'].ewm(
            span=self.signal_period,
            adjust=False
        ).mean()

        # 히스토그램 = MACD선 - 시그널선
        data['macd_histogram'] = data['macd'] - data['macd_signal']

        return data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        MACD 기반 매매 신호를 생성합니다.

        Args:
            data (pd.DataFrame): MACD 지표가 계산된 데이터

        Returns:
            pd.DataFrame: trade_signal 컬럼이 추가된 데이터
                - trade_signal = 1: MACD선 > 시그널선 (매수 신호)
                - trade_signal = -1: MACD선 < 시그널선 (매도 신호)
                - trade_signal = 0: 신호 없음
        """
        # trade_signal 컬럼 초기화
        data['trade_signal'] = 0

        # MACD선 > 시그널선 → 매수 신호
        data.loc[data['macd'] > data['macd_signal'], 'trade_signal'] = 1

        # MACD선 < 시그널선 → 매도 신호
        data.loc[data['macd'] < data['macd_signal'], 'trade_signal'] = -1

        return data

    def get_strategy_name(self) -> str:
        """
        전략 이름을 반환합니다.

        Returns:
            str: 전략 이름
        """
        return f"MACD ({self.fast_period}/{self.slow_period}/{self.signal_period})"
