"""
Refactored Backtest Main

리팩토링된 모듈을 사용하여 백테스트를 실행합니다.
"""

import yaml
import pandas as pd
from core.data_loader import DataLoader
from core.backtest_engine import BacktestEngine
from core.performance import PerformanceAnalyzer
from strategies.factory import StrategyFactory


def load_config(config_path='config.yml'):
    """YAML 설정 파일을 로드합니다."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def save_to_excel(data, performance, filename="backtest_results_refactored.xlsx"):
    """결과를 Excel 파일로 저장합니다."""
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # 시계열 데이터 시트
        sheet1_cols = ['open', 'high', 'low', 'close', 'volume', 'short_ma', 'long_ma',
                       'trade_signal', 'trade_log', 'num_stocks', 'holding_size',
                       'holding_return(%)', 'cash', 'total_assets', 'cumulative_return(%)']
        data[sheet1_cols].to_excel(writer, sheet_name='시계열 데이터')

        # 성과 종합 시트
        performance_df = pd.DataFrame(list(performance.items()), columns=['지표', '값'])
        performance_df.to_excel(writer, sheet_name='성과 종합', index=False)


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("리팩토링된 백테스트 시스템 실행")
    print("=" * 60)

    # 1. 설정 로드
    print("\n[1/6] 설정 파일 로드 중...")
    config = load_config()
    strategy_config = config['strategy']
    print(f"✓ 설정 로드 완료")
    print(f"  - 종목: {strategy_config['ticker']}")
    print(f"  - 기간: {strategy_config['start_date']} ~ {strategy_config['end_date']}")
    print(f"  - 초기 자본: ${strategy_config['initial_capital']}")

    # 2. 데이터 로딩
    print(f"\n[2/6] {strategy_config['ticker']} 데이터 로딩 중...")
    data_loader = DataLoader()
    data = data_loader.load_data(
        ticker=strategy_config['ticker'],
        start_date=strategy_config['start_date'],
        end_date=strategy_config['end_date'],
        interval=strategy_config['time_period']
    )
    print(f"✓ 데이터 로드 완료: {len(data)}개 캔들")

    # 3. 전략 생성
    print("\n[3/6] 전략 생성 중...")
    strategy = StrategyFactory.create_strategy(
        strategy_type='golden_cross',
        params={
            'short_ma': strategy_config['short_ma'],
            'long_ma': strategy_config['long_ma']
        }
    )
    print(f"✓ 전략 생성 완료: {strategy.get_strategy_name()}")

    # 4. 백테스트 실행
    print("\n[4/6] 백테스트 실행 중...")
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=strategy_config['initial_capital'],
        trade_unit_size=strategy_config['trade_unit_size']
    )
    backtest_result, trades = engine.run(data)
    print(f"✓ 백테스트 완료: {len(trades)}건의 거래 발생")

    # 5. 성과 분석
    print("\n[5/6] 성과 지표 계산 중...")
    analyzer = PerformanceAnalyzer(
        data=backtest_result,
        trades=trades,
        initial_capital=strategy_config['initial_capital']
    )
    performance = analyzer.calculate_all()
    print("✓ 성과 분석 완료")

    # 6. 결과 저장
    output_filename = f"backtest_result_{strategy_config['ticker']}_refactored.xlsx"
    print(f"\n[6/6] 결과를 {output_filename} 파일로 저장 중...")
    save_to_excel(backtest_result, performance, filename=output_filename)
    print("✓ 저장 완료")

    # 결과 출력
    print("\n" + "=" * 60)
    print("백테스트 결과 요약")
    print("=" * 60)
    for key, value in performance.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")

    print("\n" + "=" * 60)
    print("✅ 백테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
