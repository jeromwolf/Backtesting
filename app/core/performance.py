"""
Performance Analyzer Module

백테스트 결과의 성과 지표를 계산합니다.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any


class PerformanceAnalyzer:
    """
    성과 분석 클래스

    백테스트 결과를 바탕으로 다양한 성과 지표를 계산합니다.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        trades: List[Dict],
        initial_capital: float
    ):
        """
        성과 분석기 초기화

        Args:
            data (pd.DataFrame): 백테스트 결과 데이터
            trades (List[Dict]): 거래 내역 리스트
            initial_capital (float): 초기 자본금
        """
        self.data = data
        self.trades = trades
        self.initial_capital = initial_capital

    def calculate_all(self) -> Dict[str, Any]:
        """
        모든 성과 지표를 계산합니다.

        Returns:
            Dict[str, Any]: 성과 지표 딕셔너리
                - 최종 누적 수익률 (%)
                - 총 거래 횟수
                - 승률 (%)
                - MDD (%)
                - MDD 발생일
                - CAGR (%)
                - 샤프 지수
        """
        final_assets = self.data['total_assets'].iloc[-1]
        cumulative_return = ((final_assets / self.initial_capital) - 1) * 100

        # 각 지표 계산
        mdd, mdd_date = self._calculate_mdd()
        total_trades, win_rate = self._calculate_win_rate()
        cagr = self._calculate_cagr(final_assets)
        sharpe_ratio = self._calculate_sharpe_ratio()

        performance = {
            "최종 누적 수익률 (%)": cumulative_return,
            "총 거래 횟수": total_trades,
            "승률 (%)": win_rate,
            "MDD (%)": mdd,
            "MDD 발생일": mdd_date,
            "CAGR (%)": cagr,
            "샤프 지수": sharpe_ratio
        }

        return performance

    def _calculate_mdd(self) -> tuple[float, pd.Timestamp]:
        """
        MDD (Maximum Drawdown, 최대 낙폭)를 계산합니다.

        Returns:
            tuple[float, pd.Timestamp]:
                - MDD 값 (%)
                - MDD가 발생한 날짜
        """
        # 누적 최고점 (Peak) 계산
        self.data['peak'] = self.data['total_assets'].cummax()

        # Drawdown 계산 (현재 자산 / 최고점 - 1)
        self.data['drawdown'] = (self.data['total_assets'] / self.data['peak']) - 1

        # MDD는 가장 큰 낙폭 (음수 중 가장 작은 값)
        mdd = self.data['drawdown'].min() * 100
        mdd_date = self.data['drawdown'].idxmin()

        return mdd, mdd_date

    def _calculate_win_rate(self) -> tuple[int, float]:
        """
        총 거래 횟수와 승률을 계산합니다.

        Returns:
            tuple[int, float]:
                - 총 거래 횟수 (매수 기준)
                - 승률 (%)
        """
        # 매수 거래만 추출
        buy_trades = [t for t in self.trades if t['type'] == 'BUY']
        total_trades = len(buy_trades)

        if total_trades == 0:
            return 0, 0.0

        wins = 0

        # 각 매수 거래에 대해 승패 판정
        for i in range(total_trades):
            buy_trade = buy_trades[i]

            # 해당 매수 이후의 매도 거래 찾기
            sell_trade = next(
                (t for t in self.trades
                 if t['type'] == 'SELL' and t['date'] > buy_trade['date']),
                None
            )

            if sell_trade:
                # 매도가 매수가보다 높으면 수익
                if sell_trade['price'] > buy_trade['price']:
                    wins += 1
            else:
                # 매도되지 않은 경우 (마지막 매수 거래)
                # 최종일 종가로 판정
                if i == total_trades - 1:
                    final_price = self.data['close'].iloc[-1]
                    if final_price > buy_trade['price']:
                        wins += 1

        win_rate = (wins / total_trades) * 100

        return total_trades, win_rate

    def _calculate_cagr(self, final_assets: float) -> float:
        """
        CAGR (Compound Annual Growth Rate, 연평균 복리 수익률)를 계산합니다.

        Args:
            final_assets (float): 최종 자산

        Returns:
            float: CAGR (%)
        """
        # 투자 기간 (일 수)
        days = (self.data.index[-1] - self.data.index[0]).days

        if days <= 0:
            return 0.0

        # CAGR 공식: (최종자산 / 초기자산) ^ (365 / 일수) - 1
        cagr = ((final_assets / self.initial_capital) ** (365.0 / days) - 1) * 100

        return cagr

    def _calculate_sharpe_ratio(self) -> float:
        """
        샤프 지수 (Sharpe Ratio)를 계산합니다.
        무위험 수익률은 0%로 가정합니다.

        Returns:
            float: 샤프 지수
        """
        # 일별 수익률 계산
        returns = self.data['total_assets'].pct_change().dropna()

        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        # 샤프 지수 = sqrt(252) * (평균 수익률 / 수익률 표준편차)
        # 252: 연간 거래일 수
        sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std())

        return sharpe_ratio

    def get_summary_dataframe(self) -> pd.DataFrame:
        """
        성과 지표를 데이터프레임으로 반환합니다.

        Returns:
            pd.DataFrame: 성과 지표 요약 테이블
        """
        performance = self.calculate_all()
        df = pd.DataFrame(
            list(performance.items()),
            columns=['지표', '값']
        )
        return df
