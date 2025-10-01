"""
Bollinger Bands Strategy

볼린저 밴드를 사용한 전략입니다.
가격이 하단 밴드를 터치하면 매수, 상단 밴드를 터치하면 매도합니다.
"""

import pandas as pd
from .base import TradingStrategy


class BollingerStrategy(TradingStrategy):
    """
    볼린저 밴드 전략

    중심선(이동평균)을 기준으로 상단/하단 밴드를 계산하고,
    가격이 밴드를 벗어나면 평균 회귀를 예상하여 매매합니다.

    매수 신호: 가격 < 하단 밴드
    매도 신호: 가격 > 상단 밴드
    """

    def __init__(self, params: dict):
        """
        볼린저 밴드 전략 초기화

        Args:
            params (dict): 전략 파라미터
                - period (int): 이동평균 기간 (기본: 20)
                - std_dev (float): 표준편차 배수 (기본: 2.0)

        Example:
            strategy = BollingerStrategy({
                'period': 20,
                'std_dev': 2.0
            })
        """
        super().__init__(params)
        self.period = params.get('period', 20)
        self.std_dev = params.get('std_dev', 2.0)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        볼린저 밴드를 계산합니다.

        볼린저 밴드 계산:
        1. 중심선(Middle Band) = N일 이동평균
        2. 상단 밴드(Upper Band) = 중심선 + (표준편차 × k)
        3. 하단 밴드(Lower Band) = 중심선 - (표준편차 × k)

        Args:
            data (pd.DataFrame): OHLCV 데이터

        Returns:
            pd.DataFrame: 볼린저 밴드 지표가 추가된 데이터
                - bb_middle: 중심선 (이동평균)
                - bb_upper: 상단 밴드
                - bb_lower: 하단 밴드
                - bb_width: 밴드 폭 (변동성 지표)
        """
        # 중심선: 이동평균
        data['bb_middle'] = data['close'].rolling(window=self.period).mean()

        # 표준편차 계산
        rolling_std = data['close'].rolling(window=self.period).std()

        # 상단/하단 밴드
        data['bb_upper'] = data['bb_middle'] + (rolling_std * self.std_dev)
        data['bb_lower'] = data['bb_middle'] - (rolling_std * self.std_dev)

        # 밴드 폭 (변동성 지표)
        data['bb_width'] = data['bb_upper'] - data['bb_lower']

        return data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        볼린저 밴드 기반 매매 신호를 생성합니다.

        Args:
            data (pd.DataFrame): 볼린저 밴드가 계산된 데이터

        Returns:
            pd.DataFrame: trade_signal 컬럼이 추가된 데이터
                - trade_signal = 1: 가격이 하단 밴드 이하 (매수 신호)
                - trade_signal = -1: 가격이 상단 밴드 이상 (매도 신호)
                - trade_signal = 0: 밴드 내부 (중립)
        """
        # trade_signal 컬럼 초기화
        data['trade_signal'] = 0

        # 하단 밴드 돌파: 가격 < 하단 밴드 → 매수 신호 (과매도)
        data.loc[data['close'] < data['bb_lower'], 'trade_signal'] = 1

        # 상단 밴드 돌파: 가격 > 상단 밴드 → 매도 신호 (과매수)
        data.loc[data['close'] > data['bb_upper'], 'trade_signal'] = -1

        return data

    def get_strategy_name(self) -> str:
        """
        전략 이름을 반환합니다.

        Returns:
            str: 전략 이름
        """
        return f"Bollinger Bands ({self.period}, {self.std_dev}σ)"
