"""
Data Loader Module

yfinance를 사용하여 주식 데이터를 로드하고 전처리합니다.
"""

import yfinance as yf
import pandas as pd
from typing import Optional


class DataLoader:
    """
    주식 데이터 로더 클래스

    yfinance API를 사용하여 주식 데이터를 다운로드하고 정규화합니다.
    """

    def __init__(self):
        """DataLoader 초기화"""
        pass

    def load_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = '1d'
    ) -> pd.DataFrame:
        """
        주식 데이터를 로드합니다.

        Args:
            ticker (str): 종목 심볼 (예: 'TSLA', 'AAPL')
            start_date (str): 시작일 (YYYY-MM-DD)
            end_date (str): 종료일 (YYYY-MM-DD)
            interval (str): 시간 간격
                - '1m': 1분봉
                - '5m': 5분봉
                - '1h': 1시간봉
                - '1d': 일봉 (기본값)

        Returns:
            pd.DataFrame: 정규화된 OHLCV 데이터
                컬럼: open, high, low, close, volume

        Raises:
            ValueError: 데이터가 비어있거나 로드에 실패한 경우

        Example:
            loader = DataLoader()
            data = loader.load_data('TSLA', '2024-01-01', '2025-10-01')
        """
        try:
            # yfinance로 데이터 다운로드
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=False  # 진행률 바 비활성화
            )

            # 데이터가 비어있는지 확인
            if data.empty:
                raise ValueError(
                    f"데이터를 불러올 수 없습니다: {ticker} "
                    f"({start_date} ~ {end_date})"
                )

            # MultiIndex 처리 (yfinance가 여러 종목을 다운로드할 때 발생)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            # 컬럼명을 소문자로 정규화
            data.columns = [col.lower() for col in data.columns]

            # 필수 컬럼 확인
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in data.columns]

            if missing_columns:
                raise ValueError(
                    f"필수 컬럼이 없습니다: {missing_columns}"
                )

            return data

        except Exception as e:
            raise ValueError(f"데이터 로드 중 오류 발생: {str(e)}")

    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        데이터 유효성을 검사합니다.

        Args:
            data (pd.DataFrame): 검증할 데이터

        Returns:
            bool: 유효하면 True, 아니면 False
        """
        if data.empty:
            return False

        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            return False

        # NaN 값 확인
        if data[required_columns].isnull().any().any():
            return False

        return True
