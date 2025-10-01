"""
새로운 전략들 테스트

RSI, Bollinger Bands, MACD 전략을 테스트합니다.
"""

import yaml
from core.data_loader import DataLoader
from core.backtest_engine import BacktestEngine
from core.performance import PerformanceAnalyzer
from strategies.factory import StrategyFactory


def test_strategy(strategy_type, strategy_params, ticker='TSLA'):
    """단일 전략 테스트"""
    print(f"\n{'='*60}")
    print(f"{strategy_type.upper()} 전략 테스트")
    print(f"{'='*60}")

    # 데이터 로드
    data_loader = DataLoader()
    data = data_loader.load_data(
        ticker=ticker,
        start_date='2024-01-01',
        end_date='2025-10-01',
        interval='1d'
    )
    print(f"✓ 데이터 로드 완료: {len(data)}개 캔들")

    # 전략 생성
    strategy = StrategyFactory.create_strategy(strategy_type, strategy_params)
    print(f"✓ 전략 생성: {strategy.get_strategy_name()}")

    # 백테스트 실행
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=1000,
        trade_unit_size='full'
    )
    backtest_result, trades = engine.run(data)
    print(f"✓ 백테스트 완료: {len(trades)}건의 거래")

    # 성과 분석
    analyzer = PerformanceAnalyzer(
        data=backtest_result,
        trades=trades,
        initial_capital=1000
    )
    performance = analyzer.calculate_all()

    # 결과 출력
    print(f"\n[성과 지표]")
    print(f"  누적 수익률: {performance['최종 누적 수익률 (%)']:.2f}%")
    print(f"  거래 횟수: {performance['총 거래 횟수']}")
    print(f"  승률: {performance['승률 (%)']:.2f}%")
    print(f"  MDD: {performance['MDD (%)']:.2f}%")
    print(f"  CAGR: {performance['CAGR (%)']:.2f}%")
    print(f"  Sharpe: {performance['샤프 지수']:.2f}")

    return performance


def main():
    print("🚀 새로운 전략 테스트 시작")
    print("="*60)

    # 1. RSI 전략 테스트
    rsi_performance = test_strategy(
        strategy_type='rsi',
        strategy_params={
            'rsi_period': 14,
            'oversold': 30,
            'overbought': 70
        }
    )

    # 2. Bollinger Bands 전략 테스트
    bollinger_performance = test_strategy(
        strategy_type='bollinger',
        strategy_params={
            'period': 20,
            'std_dev': 2.0
        }
    )

    # 3. MACD 전략 테스트
    macd_performance = test_strategy(
        strategy_type='macd',
        strategy_params={
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }
    )

    # 4. Golden Cross 전략 (비교용)
    golden_cross_performance = test_strategy(
        strategy_type='golden_cross',
        strategy_params={
            'short_ma': 20,
            'long_ma': 60
        }
    )

    # 전략 비교
    print(f"\n{'='*60}")
    print("전략 비교 요약")
    print(f"{'='*60}")

    strategies = {
        'RSI': rsi_performance,
        'Bollinger': bollinger_performance,
        'MACD': macd_performance,
        'Golden Cross': golden_cross_performance
    }

    print(f"\n{'전략':<15} {'수익률':<10} {'거래수':<8} {'승률':<10} {'MDD':<10} {'Sharpe':<8}")
    print("-" * 60)

    for name, perf in strategies.items():
        print(
            f"{name:<15} "
            f"{perf['최종 누적 수익률 (%)']:>8.2f}% "
            f"{perf['총 거래 횟수']:>6.0f} "
            f"{perf['승률 (%)']:>8.2f}% "
            f"{perf['MDD (%)']:>8.2f}% "
            f"{perf['샤프 지수']:>6.2f}"
        )

    # 최고 성과 전략
    best_strategy = max(strategies.items(), key=lambda x: x[1]['최종 누적 수익률 (%)'])
    print(f"\n🏆 최고 수익률 전략: {best_strategy[0]} ({best_strategy[1]['최종 누적 수익률 (%)']:.2f}%)")

    print(f"\n{'='*60}")
    print("✅ 모든 전략 테스트 완료!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
