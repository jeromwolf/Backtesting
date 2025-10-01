"""
Buy and Hold Strategy

매수 후 보유 전략 (벤치마크)
가장 처음에 전액 매수하고 끝까지 보유합니다.
"""

import pandas as pd
from .base import TradingStrategy


class BuyAndHoldStrategy(TradingStrategy):
    """
    Buy and Hold 전략 (벤치마크)

    첫 거래일에 전액 매수하고 마지막 날까지 보유합니다.
    다른 전략들의 성과를 비교하기 위한 기준선(벤치마크)으로 사용됩니다.

    매수 신호: 첫 거래일에만 1번
    매도 신호: 없음 (계속 보유)
    """

    def __init__(self, params: dict = None):
        """
        Buy and Hold 전략 초기화

        Args:
            params (dict): 전략 파라미터 (사용하지 않음)

        Example:
            strategy = BuyAndHoldStrategy()
        """
        super().__init__(params or {})

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        지표를 계산합니다.

        Buy and Hold는 별도의 기술적 지표가 필요 없으므로
        아무 것도 계산하지 않습니다.

        Args:
            data (pd.DataFrame): OHLCV 데이터

        Returns:
            pd.DataFrame: 원본 데이터 그대로 반환
        """
        # 별도의 지표 계산 없음
        return data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        매매 신호를 생성합니다.

        첫 거래일에만 매수 신호(1)를 생성하고,
        나머지는 보유 신호(1)를 유지합니다.

        Args:
            data (pd.DataFrame): 데이터프레임

        Returns:
            pd.DataFrame: trade_signal 컬럼이 추가된 데이터
                - 첫 번째 날: trade_signal = 0 (준비)
                - 두 번째 날부터: trade_signal = 1 (매수 후 계속 보유)
        """
        # 초기화
        data['trade_signal'] = 0

        # 첫 거래일(인덱스 1)부터 끝까지 매수 신호
        # 인덱스 0은 0으로 유지하여 인덱스 1에서 신호 변경(0->1)이 발생
        if len(data) > 1:
            data.iloc[1:, data.columns.get_loc('trade_signal')] = 1

        return data

    def get_strategy_name(self) -> str:
        """
        전략 이름을 반환합니다.

        Returns:
            str: 전략 이름
        """
        return "Buy and Hold (Benchmark)"
