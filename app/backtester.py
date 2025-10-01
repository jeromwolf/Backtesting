
import yaml
import yfinance as yf
import pandas as pd
import numpy as np

def load_config(config_path='config.yml'):
    """YAML 설정 파일을 로드합니다."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_data(ticker, start_date, end_date, interval='1d'):
    """yfinance를 통해 주식 데이터를 가져옵니다."""
    data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    # yfinance에서 컬럼명이 소문자로 바뀜에 따라 대응
    data.columns = [col.lower() for col in data.columns]
    return data

def calculate_indicators(data, short_ma, long_ma):
    """이동평균선과 매매 신호를 계산합니다."""
    data['short_ma'] = data['close'].rolling(window=short_ma).mean()
    data['long_ma'] = data['close'].rolling(window=long_ma).mean()
    
    # 골든크로스: 단기 이평선이 장기 이평선을 상향 돌파
    # 데드크로스: 단기 이평선이 장기 이평선을 하향 돌파
    data['trade_signal'] = 0
    data.loc[data['short_ma'] > data['long_ma'], 'trade_signal'] = 1  # 매수 신호
    data.loc[data['short_ma'] < data['long_ma'], 'trade_signal'] = -1 # 매도 신호
    
    return data

def run_backtest(data, initial_capital, trade_unit_size):
    """백테스트 시뮬레이션을 실행합니다."""
    cash = initial_capital
    num_stocks = 0
    position_value = 0
    
    data['trade_log'] = ''
    data['num_stocks'] = 0
    data['holding_size'] = 0.0
    data['cash'] = float(initial_capital)
    data['total_assets'] = float(initial_capital)
    
    trades = []
    
    for i in range(1, len(data)):
        # 신호 변경 감지
        prev_signal = data['trade_signal'].iloc[i-1]
        current_signal = data['trade_signal'].iloc[i]
        
        # 매수 (데드크로스 -> 골든크로스)
        if prev_signal <= 0 and current_signal == 1:
            price = data['close'].iloc[i]
            
            # 거래 단위 결정
            buy_amount = 0
            if trade_unit_size == 'full':
                buy_amount = cash
            else:
                buy_amount = trade_unit_size
            
            # [중요] 매수 신호 처리시, 해당 종목 1주 단가가 단위거래금액을 초과할 경우,
            # 가용 금액 허용 범위안에서 최소 1주 단위 거래 진행
            if price > buy_amount and cash >= price:
                stocks_to_buy = 1
            elif cash >= buy_amount:
                stocks_to_buy = int(buy_amount // price)
            else:
                stocks_to_buy = 0

            if stocks_to_buy > 0:
                cost = stocks_to_buy * price
                cash -= cost
                num_stocks += stocks_to_buy
                position_value = num_stocks * price
                
                data.loc[data.index[i], 'trade_log'] = 'BUY'
                trades.append({'type': 'BUY', 'date': data.index[i], 'price': price, 'shares': stocks_to_buy})

        # 매도 (골든크로스 -> 데드크로스)
        elif prev_signal >= 0 and current_signal == -1:
            if num_stocks > 0:
                price = data['close'].iloc[i]
                sell_value = num_stocks * price
                cash += sell_value
                
                data.loc[data.index[i], 'trade_log'] = 'SELL'
                trades.append({'type': 'SELL', 'date': data.index[i], 'price': price, 'shares': num_stocks})
                
                num_stocks = 0
                position_value = 0

        # 일별 자산 업데이트
        position_value = num_stocks * data['close'].iloc[i]
        data.loc[data.index[i], 'num_stocks'] = num_stocks
        data.loc[data.index[i], 'holding_size'] = position_value
        data.loc[data.index[i], 'cash'] = cash
        data.loc[data.index[i], 'total_assets'] = cash + position_value

    data['cumulative_return(%)'] = ((data['total_assets'] / initial_capital) - 1) * 100
    
    # 포지션 수익률 계산
    buy_price = 0
    data['holding_return(%)'] = 0.0
    for i in range(len(data)):
        if data['trade_log'].iloc[i] == 'BUY':
            buy_price = data['close'].iloc[i]
        
        if buy_price > 0 and data['num_stocks'].iloc[i] > 0:
             data.loc[data.index[i], 'holding_return(%)'] = ((data['close'].iloc[i] / buy_price) - 1) * 100
        
        if data['trade_log'].iloc[i] == 'SELL':
            buy_price = 0

    return data, trades

def calculate_performance(data, trades, initial_capital):
    """성과 지표를 계산합니다."""
    final_assets = data['total_assets'].iloc[-1]
    cumulative_return = ((final_assets / initial_capital) - 1) * 100
    
    # MDD (최대 낙폭)
    data['peak'] = data['total_assets'].cummax()
    data['drawdown'] = (data['total_assets'] / data['peak']) - 1
    mdd = data['drawdown'].min() * 100
    mdd_date = data['drawdown'].idxmin()

    # 총 거래 횟수 및 승률
    buy_trades = [t for t in trades if t['type'] == 'BUY']
    total_trades = len(buy_trades)
    wins = 0
    
    for i in range(total_trades):
        buy_trade = buy_trades[i]
        sell_trade = next((t for t in trades if t['type'] == 'SELL' and t['date'] > buy_trade['date']), None)
        
        if sell_trade:
            if sell_trade['price'] > buy_trade['price']:
                wins += 1
        # 매도되지 않은 경우, 최종일 종가로 PNL 계산
        elif i == total_trades - 1 and not sell_trade:
             if data['close'].iloc[-1] > buy_trade['price']:
                wins += 1

    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
    
    # CAGR (연평균 복리 수익률)
    days = (data.index[-1] - data.index[0]).days
    cagr = ((final_assets / initial_capital) ** (365.0 / days) - 1) * 100 if days > 0 else 0
    
    # 샤프 지수 (무위험 수익률 0% 가정)
    returns = data['total_assets'].pct_change().dropna()
    sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std()) if returns.std() != 0 else 0

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

def save_to_excel(data, performance, filename="backtest_results.xlsx"):
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
    # 1. 설정 로드
    config = load_config()
    strategy_config = config['strategy']
    
    # 2. 데이터 가져오기
    print(f"{strategy_config['ticker']} 데이터 로딩 중...")
    data = get_data(
        ticker=strategy_config['ticker'],
        start_date=strategy_config['start_date'],
        end_date=strategy_config['end_date'],
        interval=strategy_config['time_period']
    )
    
    # 3. 지표 계산
    print("이동평균선 및 매매 신호 계산 중...")
    data = calculate_indicators(
        data=data,
        short_ma=strategy_config['short_ma'],
        long_ma=strategy_config['long_ma']
    )
    
    # 4. 백테스트 실행
    print("백테스트 시뮬레이션 실행 중...")
    backtest_result, trades = run_backtest(
        data=data,
        initial_capital=strategy_config['initial_capital'],
        trade_unit_size=strategy_config['trade_unit_size']
    )
    
    # 5. 성과 분석
    print("성과 지표 계산 중...")
    performance = calculate_performance(
        data=backtest_result,
        trades=trades,
        initial_capital=strategy_config['initial_capital']
    )
    
    # 6. 결과 저장
    output_filename = f"backtest_result_{strategy_config['ticker']}.xlsx"
    print(f"결과를 {output_filename} 파일로 저장 중...")
    save_to_excel(backtest_result, performance, filename=output_filename)
    
    print("\n백테스트 완료!")
    print("--- 성과 요약 ---")
    for key, value in performance.items():
        if isinstance(value, (int, float)):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()
