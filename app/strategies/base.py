"""
Trading Strategy Base Class

모든 트레이딩 전략의 추상 기본 클래스입니다.
새로운 전략을 추가하려면 이 클래스를 상속받아 구현하세요.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict


class TradingStrategy(ABC):
    """
    트레이딩 전략 추상 기본 클래스

    모든 전략은 이 클래스를 상속받아 다음 메서드들을 구현해야 합니다:
    - calculate_indicators: 기술적 지표 계산
    - generate_signals: 매매 신호 생성
    - get_strategy_name: 전략 이름 반환
    """

    def __init__(self, params: Dict):
        """
        전략 초기화

        Args:
            params (Dict): 전략 파라미터 딕셔너리
                예: {'short_ma': 20, 'long_ma': 60}
        """
        self.params = params

    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        기술적 지표를 계산합니다.

        Args:
            data (pd.DataFrame): OHLCV 데이터
                필수 컬럼: open, high, low, close, volume

        Returns:
            pd.DataFrame: 지표가 추가된 데이터프레임
                예: short_ma, long_ma, rsi, bollinger_upper 등

        Example:
            data['short_ma'] = data['close'].rolling(window=20).mean()
            return data
        """
        pass

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        매매 신호를 생성합니다.

        Args:
            data (pd.DataFrame): 지표가 계산된 데이터프레임

        Returns:
            pd.DataFrame: 'trade_signal' 컬럼이 추가된 데이터프레임
                trade_signal 값:
                    1: 매수 신호
                   -1: 매도 신호
                    0: 신호 없음

        Example:
            data['trade_signal'] = 0
            data.loc[data['short_ma'] > data['long_ma'], 'trade_signal'] = 1
            data.loc[data['short_ma'] < data['long_ma'], 'trade_signal'] = -1
            return data
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        전략 이름을 반환합니다.

        Returns:
            str: 전략 이름 (예: 'Golden Cross', 'RSI', 'Bollinger Bands')
        """
        pass
