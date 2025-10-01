"""
Backtest Engine Module

트레이딩 전략의 백테스트를 실행하는 엔진입니다.
"""

import pandas as pd
from typing import List, Dict, Union
from strategies.base import TradingStrategy


class BacktestEngine:
    """
    백테스트 엔진 클래스

    주어진 전략에 따라 과거 데이터로 거래를 시뮬레이션합니다.
    """

    def __init__(
        self,
        strategy: TradingStrategy,
        initial_capital: float,
        trade_unit_size: Union[float, str]
    ):
        """
        백테스트 엔진 초기화

        Args:
            strategy (TradingStrategy): 적용할 트레이딩 전략
            initial_capital (float): 초기 자본금
            trade_unit_size (Union[float, str]): 거래 단위
                - float: 고정 금액 (예: 100)
                - 'full': 가용 금액 전체
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.trade_unit_size = trade_unit_size

        # 초기 상태 변수
        self.cash = initial_capital
        self.num_stocks = 0
        self.position_value = 0.0
        self.trades: List[Dict] = []

    def run(self, data: pd.DataFrame) -> tuple[pd.DataFrame, List[Dict]]:
        """
        백테스트를 실행합니다.

        Args:
            data (pd.DataFrame): OHLCV 데이터

        Returns:
            tuple[pd.DataFrame, List[Dict]]:
                - 백테스트 결과가 포함된 데이터프레임
                - 거래 내역 리스트
        """
        # 전략 적용: 지표 계산 및 신호 생성
        data = self.strategy.calculate_indicators(data)
        data = self.strategy.generate_signals(data)

        # 백테스트 컬럼 초기화
        data = self._initialize_columns(data)

        # 거래 시뮬레이션
        data = self._simulate_trades(data)

        # 추가 지표 계산
        data = self._calculate_returns(data)

        return data, self.trades

    def _initialize_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """백테스트에 필요한 컬럼을 초기화합니다."""
        data['trade_log'] = ''
        data['num_stocks'] = 0
        data['holding_size'] = 0.0
        data['cash'] = float(self.initial_capital)
        data['total_assets'] = float(self.initial_capital)
        data['holding_return(%)'] = 0.0

        # 첫 번째 행의 초기 상태 설정
        if len(data) > 0:
            data.loc[data.index[0], 'cash'] = float(self.initial_capital)
            data.loc[data.index[0], 'total_assets'] = float(self.initial_capital)

        return data

    def _simulate_trades(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        거래를 시뮬레이션합니다.

        Args:
            data (pd.DataFrame): 신호가 포함된 데이터

        Returns:
            pd.DataFrame: 거래 결과가 반영된 데이터
        """
        for i in range(1, len(data)):
            # 이전 신호와 현재 신호 확인
            prev_signal = data['trade_signal'].iloc[i - 1]
            current_signal = data['trade_signal'].iloc[i]

            # 매수 신호 (데드크로스 -> 골든크로스)
            if prev_signal <= 0 and current_signal == 1:
                self._execute_buy(data, i)

            # 매도 신호 (골든크로스 -> 데드크로스)
            elif prev_signal >= 0 and current_signal == -1:
                self._execute_sell(data, i)

            # 일별 자산 업데이트
            self._update_daily_status(data, i)

        return data

    def _execute_buy(self, data: pd.DataFrame, index: int) -> None:
        """
        매수를 실행합니다.

        Args:
            data (pd.DataFrame): 데이터프레임
            index (int): 현재 인덱스
        """
        price = data['close'].iloc[index]

        # 거래 단위 결정
        if self.trade_unit_size == 'full':
            buy_amount = self.cash
        else:
            buy_amount = float(self.trade_unit_size)

        # 주식 수 계산
        # [중요] 1주 단가가 단위거래금액을 초과하는 경우 처리
        if price > buy_amount and self.cash >= price:
            # 1주도 못 살 금액이지만, 현금이 1주는 살 수 있으면 1주 매수
            stocks_to_buy = 1
        elif self.cash >= buy_amount:
            # 정상적인 경우: 거래 단위 금액으로 살 수 있는 주식 수 (버림)
            stocks_to_buy = int(buy_amount // price)
        else:
            # 현금 부족
            stocks_to_buy = 0

        # 매수 실행
        if stocks_to_buy > 0:
            cost = stocks_to_buy * price
            self.cash -= cost
            self.num_stocks += stocks_to_buy
            self.position_value = self.num_stocks * price

            # 거래 기록
            data.loc[data.index[index], 'trade_log'] = 'BUY'
            self.trades.append({
                'type': 'BUY',
                'date': data.index[index],
                'price': price,
                'shares': stocks_to_buy
            })

    def _execute_sell(self, data: pd.DataFrame, index: int) -> None:
        """
        매도를 실행합니다.

        Args:
            data (pd.DataFrame): 데이터프레임
            index (int): 현재 인덱스
        """
        if self.num_stocks > 0:
            price = data['close'].iloc[index]
            sell_value = self.num_stocks * price
            self.cash += sell_value

            # 거래 기록
            data.loc[data.index[index], 'trade_log'] = 'SELL'
            self.trades.append({
                'type': 'SELL',
                'date': data.index[index],
                'price': price,
                'shares': self.num_stocks
            })

            # 포지션 청산
            self.num_stocks = 0
            self.position_value = 0

    def _update_daily_status(self, data: pd.DataFrame, index: int) -> None:
        """
        일별 자산 상태를 업데이트합니다.

        Args:
            data (pd.DataFrame): 데이터프레임
            index (int): 현재 인덱스
        """
        # 포지션 가치 업데이트
        self.position_value = self.num_stocks * data['close'].iloc[index]

        # 데이터프레임에 기록
        data.loc[data.index[index], 'num_stocks'] = self.num_stocks
        data.loc[data.index[index], 'holding_size'] = self.position_value
        data.loc[data.index[index], 'cash'] = self.cash
        data.loc[data.index[index], 'total_assets'] = self.cash + self.position_value

    def _calculate_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        수익률을 계산합니다.

        Args:
            data (pd.DataFrame): 거래 결과 데이터

        Returns:
            pd.DataFrame: 수익률이 추가된 데이터
        """
        # 누적 수익률
        data['cumulative_return(%)'] = (
            (data['total_assets'] / self.initial_capital) - 1
        ) * 100

        # 포지션 수익률 (매수가 대비 현재가)
        buy_price = 0
        for i in range(len(data)):
            if data['trade_log'].iloc[i] == 'BUY':
                buy_price = data['close'].iloc[i]

            if buy_price > 0 and data['num_stocks'].iloc[i] > 0:
                data.loc[data.index[i], 'holding_return(%)'] = (
                    (data['close'].iloc[i] / buy_price) - 1
                ) * 100

            if data['trade_log'].iloc[i] == 'SELL':
                buy_price = 0

        return data
