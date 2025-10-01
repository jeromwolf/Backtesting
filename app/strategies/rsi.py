"""
RSI Strategy

RSI (Relative Strength Index) 지표를 사용한 전략입니다.
과매도/과매수 구간을 이용하여 매매 신호를 생성합니다.
"""

import pandas as pd
from .base import TradingStrategy


class RSIStrategy(TradingStrategy):
    """
    RSI 전략

    RSI 지표가 과매도 구간(기본 30)에 진입하면 매수,
    과매수 구간(기본 70)에 진입하면 매도합니다.

    매수 신호: RSI < oversold (과매도)
    매도 신호: RSI > overbought (과매수)
    """

    def __init__(self, params: dict):
        """
        RSI 전략 초기화

        Args:
            params (dict): 전략 파라미터
                - rsi_period (int): RSI 계산 기간 (기본: 14)
                - oversold (int): 과매도 기준선 (기본: 30)
                - overbought (int): 과매수 기준선 (기본: 70)

        Example:
            strategy = RSIStrategy({
                'rsi_period': 14,
                'oversold': 30,
                'overbought': 70
            })
        """
        super().__init__(params)
        self.rsi_period = params.get('rsi_period', 14)
        self.oversold = params.get('oversold', 30)
        self.overbought = params.get('overbought', 70)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        RSI 지표를 계산합니다.

        RSI 계산 공식:
        1. 상승분(Gain)과 하락분(Loss) 계산
        2. 평균 상승분과 평균 하락분 계산
        3. RS (Relative Strength) = 평균 상승분 / 평균 하락분
        4. RSI = 100 - (100 / (1 + RS))

        Args:
            data (pd.DataFrame): OHLCV 데이터

        Returns:
            pd.DataFrame: RSI 지표가 추가된 데이터
                - rsi: RSI 값 (0~100)
        """
        # 가격 변동 계산
        delta = data['close'].diff()

        # 상승분과 하락분 분리
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # 평균 상승분과 평균 하락분 계산 (Wilder's Smoothing)
        avg_gain = gain.rolling(window=self.rsi_period, min_periods=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period, min_periods=self.rsi_period).mean()

        # Wilder's Smoothing 적용 (2차 평활화)
        for i in range(self.rsi_period, len(data)):
            avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (self.rsi_period - 1) + gain.iloc[i]) / self.rsi_period
            avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (self.rsi_period - 1) + loss.iloc[i]) / self.rsi_period

        # RS (Relative Strength) 계산
        rs = avg_gain / avg_loss

        # RSI 계산
        data['rsi'] = 100 - (100 / (1 + rs))

        return data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        RSI 기반 매매 신호를 생성합니다.

        Args:
            data (pd.DataFrame): RSI 지표가 계산된 데이터

        Returns:
            pd.DataFrame: trade_signal 컬럼이 추가된 데이터
                - trade_signal = 1: 과매도 구간 (매수 신호)
                - trade_signal = -1: 과매수 구간 (매도 신호)
                - trade_signal = 0: 중립 구간
        """
        # trade_signal 컬럼 초기화
        data['trade_signal'] = 0

        # 과매도 구간: RSI < oversold → 매수 신호
        data.loc[data['rsi'] < self.oversold, 'trade_signal'] = 1

        # 과매수 구간: RSI > overbought → 매도 신호
        data.loc[data['rsi'] > self.overbought, 'trade_signal'] = -1

        return data

    def get_strategy_name(self) -> str:
        """
        전략 이름을 반환합니다.

        Returns:
            str: 전략 이름
        """
        return f"RSI ({self.rsi_period}, {self.oversold}/{self.overbought})"
