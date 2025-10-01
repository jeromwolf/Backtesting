"""
Strategy Factory

전략 인스턴스를 생성하는 팩토리 클래스입니다.
"""

from typing import Dict
from .base import TradingStrategy
from .golden_cross import GoldenCrossStrategy
from .rsi import RSIStrategy
from .bollinger import BollingerStrategy
from .macd import MACDStrategy
from .buy_and_hold import BuyAndHoldStrategy


class StrategyFactory:
    """
    전략 팩토리 클래스

    전략 타입과 파라미터를 받아 해당 전략 인스턴스를 생성합니다.
    """

    # 사용 가능한 전략 매핑
    STRATEGIES = {
        'buy_and_hold': BuyAndHoldStrategy,
        'golden_cross': GoldenCrossStrategy,
        'rsi': RSIStrategy,
        'bollinger': BollingerStrategy,
        'macd': MACDStrategy,
    }

    @staticmethod
    def create_strategy(strategy_type: str, params: Dict) -> TradingStrategy:
        """
        전략 인스턴스를 생성합니다.

        Args:
            strategy_type (str): 전략 타입
                - 'buy_and_hold': Buy and Hold 전략 (벤치마크)
                - 'golden_cross': 골든크로스 전략
                - 'rsi': RSI 전략
                - 'bollinger': 볼린저 밴드 전략
                - 'macd': MACD 전략

            params (Dict): 전략 파라미터
                예: {'short_ma': 20, 'long_ma': 60}

        Returns:
            TradingStrategy: 생성된 전략 인스턴스

        Raises:
            ValueError: 지원하지 않는 전략 타입인 경우

        Example:
            strategy = StrategyFactory.create_strategy('golden_cross', {
                'short_ma': 20,
                'long_ma': 60
            })
        """
        # 전략 타입 검증
        if strategy_type not in StrategyFactory.STRATEGIES:
            available_strategies = ', '.join(StrategyFactory.STRATEGIES.keys())
            raise ValueError(
                f"지원하지 않는 전략 타입입니다: '{strategy_type}'\n"
                f"사용 가능한 전략: {available_strategies}"
            )

        # 전략 클래스 가져오기
        strategy_class = StrategyFactory.STRATEGIES[strategy_type]

        # 전략 인스턴스 생성
        strategy = strategy_class(params)

        return strategy

    @staticmethod
    def get_available_strategies() -> list:
        """
        사용 가능한 전략 목록을 반환합니다.

        Returns:
            list: 전략 타입 리스트
        """
        return list(StrategyFactory.STRATEGIES.keys())

    @staticmethod
    def register_strategy(strategy_type: str, strategy_class: type) -> None:
        """
        새로운 전략을 등록합니다.

        Args:
            strategy_type (str): 전략 타입 이름
            strategy_class (type): 전략 클래스

        Example:
            StrategyFactory.register_strategy('custom', CustomStrategy)
        """
        if not issubclass(strategy_class, TradingStrategy):
            raise TypeError(
                f"{strategy_class.__name__}은(는) TradingStrategy를 상속받아야 합니다."
            )

        StrategyFactory.STRATEGIES[strategy_type] = strategy_class
