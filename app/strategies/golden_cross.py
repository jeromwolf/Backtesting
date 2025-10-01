"""
Golden Cross Strategy

골든크로스/데드크로스 전략을 구현합니다.
단기 이동평균선이 장기 이동평균선을 상향 돌파하면 매수,
하향 돌파하면 매도합니다.
"""

import pandas as pd
from .base import TradingStrategy


class GoldenCrossStrategy(TradingStrategy):
    """
    골든크로스 전략

    단기/장기 이동평균선의 교차를 이용한 전략입니다.

    매수 신호: 단기 이평선 > 장기 이평선 (골든크로스)
    매도 신호: 단기 이평선 < 장기 이평선 (데드크로스)
    """

    def __init__(self, params: dict):
        """
        골든크로스 전략 초기화

        Args:
            params (dict): 전략 파라미터
                - short_ma (int): 단기 이동평균 기간 (예: 20)
                - long_ma (int): 장기 이동평균 기간 (예: 60)

        Example:
            strategy = GoldenCrossStrategy({
                'short_ma': 20,
                'long_ma': 60
            })
        """
        super().__init__(params)
        self.short_ma = params.get('short_ma', 20)
        self.long_ma = params.get('long_ma', 60)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        이동평균선을 계산합니다.

        Args:
            data (pd.DataFrame): OHLCV 데이터

        Returns:
            pd.DataFrame: 이동평균선이 추가된 데이터
                - short_ma: 단기 이동평균선
                - long_ma: 장기 이동평균선
        """
        # 단기 이동평균선 계산
        data['short_ma'] = data['close'].rolling(window=self.short_ma).mean()

        # 장기 이동평균선 계산
        data['long_ma'] = data['close'].rolling(window=self.long_ma).mean()

        return data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        골든크로스/데드크로스 매매 신호를 생성합니다.

        Args:
            data (pd.DataFrame): 이동평균선이 계산된 데이터

        Returns:
            pd.DataFrame: trade_signal 컬럼이 추가된 데이터
                - trade_signal = 1: 골든크로스 (매수 신호)
                - trade_signal = -1: 데드크로스 (매도 신호)
                - trade_signal = 0: 신호 없음
        """
        # trade_signal 컬럼 초기화
        data['trade_signal'] = 0

        # 골든크로스: 단기 이평선 > 장기 이평선
        data.loc[data['short_ma'] > data['long_ma'], 'trade_signal'] = 1

        # 데드크로스: 단기 이평선 < 장기 이평선
        data.loc[data['short_ma'] < data['long_ma'], 'trade_signal'] = -1

        return data

    def get_strategy_name(self) -> str:
        """
        전략 이름을 반환합니다.

        Returns:
            str: 전략 이름
        """
        return f"Golden Cross ({self.short_ma}/{self.long_ma})"
