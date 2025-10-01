"""
Streamlit Backtest Application

웹 UI를 통해 백테스트를 실행하고 결과를 시각화합니다.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
import sys
import os

# 상위 디렉토리를 path에 추가
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from core.data_loader import DataLoader
from core.backtest_engine import BacktestEngine
from core.performance import PerformanceAnalyzer
from strategies.factory import StrategyFactory


# 페이지 설정
st.set_page_config(
    page_title="Trading Backtest System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 타이틀
st.title("📈 Trading Backtest System")
st.markdown("---")

# 사이드바: 전략 선택 및 파라미터 설정
st.sidebar.header("⚙️ 백테스트 설정")

# 1. 전략 선택
strategy_type = st.sidebar.selectbox(
    "전략 선택",
    options=['buy_and_hold', 'golden_cross', 'rsi', 'bollinger', 'macd'],
    format_func=lambda x: {
        'buy_and_hold': '💎 Buy and Hold',
        'golden_cross': '🌟 Golden Cross',
        'rsi': '📊 RSI',
        'bollinger': '📉 Bollinger Bands',
        'macd': '📈 MACD'
    }[x]
)

st.sidebar.markdown("---")

# 2. 공통 파라미터
st.sidebar.subheader("📋 공통 설정")

ticker = st.sidebar.text_input("종목 심볼", value="TSLA", help="예: TSLA, AAPL, GOOGL")

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "시작일",
        value=pd.to_datetime("2024-01-01")
    )
with col2:
    end_date = st.date_input(
        "종료일",
        value=pd.to_datetime("2025-10-01")
    )

initial_capital = st.sidebar.number_input(
    "초기 자본 ($)",
    min_value=100,
    value=1000,
    step=100
)

trade_unit = st.sidebar.radio(
    "거래 단위",
    options=['full', 100, 500, 1000],
    format_func=lambda x: '전액' if x == 'full' else f'${x}'
)

time_period = st.sidebar.selectbox(
    "봉 간격",
    options=['1d', '1h', '30m', '15m', '5m', '1m'],
    index=0,
    format_func=lambda x: {
        '1d': '일봉',
        '1h': '1시간봉',
        '30m': '30분봉',
        '15m': '15분봉',
        '5m': '5분봉',
        '1m': '1분봉'
    }[x]
)

st.sidebar.markdown("---")

# 3. 전략별 파라미터
st.sidebar.subheader("🎯 전략 파라미터")

strategy_params = {}

if strategy_type == 'buy_and_hold':
    st.sidebar.info("💎 Buy and Hold 전략은 별도의 파라미터가 필요 없습니다.\n\n첫 거래일에 전액 매수하고 끝까지 보유합니다.")

elif strategy_type == 'golden_cross':
    col1, col2 = st.sidebar.columns(2)
    with col1:
        strategy_params['short_ma'] = st.number_input(
            "단기 이평선",
            min_value=5,
            max_value=50,
            value=20
        )
    with col2:
        strategy_params['long_ma'] = st.number_input(
            "장기 이평선",
            min_value=20,
            max_value=200,
            value=60
        )

elif strategy_type == 'rsi':
    strategy_params['rsi_period'] = st.sidebar.slider(
        "RSI 기간",
        min_value=5,
        max_value=30,
        value=14
    )
    col1, col2 = st.sidebar.columns(2)
    with col1:
        strategy_params['oversold'] = st.number_input(
            "과매도",
            min_value=10,
            max_value=40,
            value=30
        )
    with col2:
        strategy_params['overbought'] = st.number_input(
            "과매수",
            min_value=60,
            max_value=90,
            value=70
        )

elif strategy_type == 'bollinger':
    strategy_params['period'] = st.sidebar.slider(
        "기간",
        min_value=10,
        max_value=50,
        value=20
    )
    strategy_params['std_dev'] = st.sidebar.slider(
        "표준편차 배수",
        min_value=1.0,
        max_value=3.0,
        value=2.0,
        step=0.1
    )

elif strategy_type == 'macd':
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        strategy_params['fast_period'] = st.number_input(
            "단기",
            min_value=5,
            max_value=20,
            value=12
        )
    with col2:
        strategy_params['slow_period'] = st.number_input(
            "장기",
            min_value=15,
            max_value=40,
            value=26
        )
    with col3:
        strategy_params['signal_period'] = st.number_input(
            "시그널",
            min_value=5,
            max_value=15,
            value=9
        )

st.sidebar.markdown("---")

# 백테스트 실행 버튼
run_backtest = st.sidebar.button("🚀 백테스트 실행", type="primary", use_container_width=True)

# 메인 영역
if run_backtest:
    try:
        with st.spinner('백테스트 실행 중...'):
            # 1. 데이터 로딩
            data_loader = DataLoader()
            data = data_loader.load_data(
                ticker=ticker,
                start_date=str(start_date),
                end_date=str(end_date),
                interval=time_period
            )

            # 2. 전략 생성
            strategy = StrategyFactory.create_strategy(strategy_type, strategy_params)

            # 3. 백테스트 실행
            engine = BacktestEngine(
                strategy=strategy,
                initial_capital=initial_capital,
                trade_unit_size=trade_unit
            )
            backtest_result, trades = engine.run(data)

            # 4. 성과 분석
            analyzer = PerformanceAnalyzer(
                data=backtest_result,
                trades=trades,
                initial_capital=initial_capital
            )
            performance = analyzer.calculate_all()

        st.success('✅ 백테스트 완료!')

        # 성과 지표 표시
        st.subheader("📊 성과 지표")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "누적 수익률",
                f"{performance['최종 누적 수익률 (%)']:.2f}%",
                delta=f"{performance['최종 누적 수익률 (%)']:.2f}%"
            )

        with col2:
            st.metric(
                "CAGR",
                f"{performance['CAGR (%)']:.2f}%"
            )

        with col3:
            st.metric(
                "MDD",
                f"{performance['MDD (%)']:.2f}%",
                delta=f"{performance['MDD (%)']:.2f}%",
                delta_color="inverse"
            )

        with col4:
            st.metric(
                "Sharpe Ratio",
                f"{performance['샤프 지수']:.2f}"
            )

        col5, col6, col7 = st.columns(3)

        with col5:
            st.metric("총 거래 횟수", f"{performance['총 거래 횟수']:.0f}")

        with col6:
            st.metric("승률", f"{performance['승률 (%)']:.2f}%")

        with col7:
            st.metric(
                "최종 자산",
                f"${backtest_result['total_assets'].iloc[-1]:.2f}"
            )

        st.markdown("---")

        # 차트 표시
        st.subheader("📈 가격 차트 & 매매 신호")

        fig = go.Figure()

        # 가격
        fig.add_trace(go.Scatter(
            x=backtest_result.index,
            y=backtest_result['close'],
            name='가격',
            line=dict(color='lightgray', width=1)
        ))

        # 전략별 지표
        if strategy_type == 'golden_cross':
            fig.add_trace(go.Scatter(
                x=backtest_result.index,
                y=backtest_result['short_ma'],
                name=f'단기 이평선 ({strategy_params["short_ma"]})',
                line=dict(color='blue', width=1)
            ))
            fig.add_trace(go.Scatter(
                x=backtest_result.index,
                y=backtest_result['long_ma'],
                name=f'장기 이평선 ({strategy_params["long_ma"]})',
                line=dict(color='orange', width=1)
            ))

        # 매수/매도 신호
        buy_signals = backtest_result[backtest_result['trade_log'] == 'BUY']
        sell_signals = backtest_result[backtest_result['trade_log'] == 'SELL']

        fig.add_trace(go.Scatter(
            x=buy_signals.index,
            y=buy_signals['close'],
            mode='markers',
            name='매수',
            marker=dict(color='green', size=10, symbol='triangle-up')
        ))

        fig.add_trace(go.Scatter(
            x=sell_signals.index,
            y=sell_signals['close'],
            mode='markers',
            name='매도',
            marker=dict(color='red', size=10, symbol='triangle-down')
        ))

        fig.update_layout(
            title=f"{ticker} - {strategy.get_strategy_name()}",
            xaxis_title="날짜",
            yaxis_title="가격 ($)",
            hovermode='x unified',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # 누적 수익률 차트
        st.subheader("💰 누적 수익률")

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=backtest_result.index,
            y=backtest_result['cumulative_return(%)'],
            fill='tozeroy',
            name='누적 수익률',
            line=dict(color='green', width=2)
        ))

        fig2.update_layout(
            xaxis_title="날짜",
            yaxis_title="수익률 (%)",
            hovermode='x unified',
            height=300
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # 데이터 테이블
        st.subheader("📋 시계열 데이터")

        # 표시할 행 수 선택
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("백테스트 결과 데이터")
        with col2:
            show_all = st.checkbox("전체 데이터 표시", value=False)

        display_columns = ['open', 'high', 'low', 'close', 'volume',
                          'trade_log', 'num_stocks', 'cash', 'total_assets',
                          'cumulative_return(%)']

        if show_all:
            st.dataframe(
                backtest_result[display_columns],
                use_container_width=True,
                height=400
            )
        else:
            st.dataframe(
                backtest_result[display_columns].tail(50),
                use_container_width=True
            )
            st.info(f"💡 최근 50개 행만 표시 중 (전체: {len(backtest_result)}개)")

        # Excel 다운로드
        st.markdown("---")
        st.subheader("📥 결과 다운로드")

        # Excel 파일 생성
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 시계열 데이터
            sheet1_cols = ['open', 'high', 'low', 'close', 'volume',
                          'trade_signal', 'trade_log', 'num_stocks', 'holding_size',
                          'holding_return(%)', 'cash', 'total_assets', 'cumulative_return(%)']

            # 전략별 지표 추가
            if strategy_type == 'golden_cross':
                sheet1_cols.insert(5, 'short_ma')
                sheet1_cols.insert(6, 'long_ma')
            elif strategy_type == 'rsi':
                sheet1_cols.insert(5, 'rsi')
            elif strategy_type == 'bollinger':
                sheet1_cols.insert(5, 'bb_upper')
                sheet1_cols.insert(6, 'bb_middle')
                sheet1_cols.insert(7, 'bb_lower')
            elif strategy_type == 'macd':
                sheet1_cols.insert(5, 'macd')
                sheet1_cols.insert(6, 'macd_signal')

            backtest_result[sheet1_cols].to_excel(writer, sheet_name='시계열 데이터')

            # 성과 종합
            performance_df = pd.DataFrame(
                list(performance.items()),
                columns=['지표', '값']
            )
            performance_df.to_excel(writer, sheet_name='성과 종합', index=False)

        excel_data = output.getvalue()

        st.download_button(
            label="📥 Excel 파일 다운로드",
            data=excel_data,
            file_name=f"backtest_{ticker}_{strategy_type}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")
        st.exception(e)

else:
    # 초기 화면
    st.info("👈 왼쪽 사이드바에서 전략과 파라미터를 설정한 후 '백테스트 실행' 버튼을 클릭하세요.")

    st.markdown("### 🎯 지원 전략")
    st.markdown("각 전략을 클릭하여 자세한 설명을 확인하세요!")

    # Buy and Hold
    with st.expander("💎 Buy and Hold (매수 후 보유) - 가장 기본적인 전략"):
        st.markdown("""
        **전략 설명**
        처음에 주식을 사서 계속 보유만 하는 방식입니다. 아무 것도 하지 않고 그냥 들고만 있는 거죠!

        **언제 매수/매도?**
        - 🟢 매수: 백테스트 시작 첫날에 전액 매수
        - 🔴 매도: 매도하지 않음 (끝까지 보유)

        **장점**
        - 가장 단순하고 쉬움
        - 장기적으로 시장이 상승하면 수익 발생
        - 거래 수수료 최소화

        **단점**
        - 하락장에서도 계속 보유하므로 손실이 클 수 있음
        - 타이밍을 전혀 고려하지 않음

        **이런 분께 추천**
        장기 투자자, 시장 타이밍을 잡기 어려운 초보 투자자
        """)

    # Golden Cross
    with st.expander("🌟 Golden Cross (골든크로스) - 이동평균선 교차 전략"):
        st.markdown("""
        **전략 설명**
        이동평균선이란? 일정 기간 동안의 평균 가격을 이은 선입니다.
        단기 이평선(예: 20일)이 장기 이평선(예: 60일)을 아래에서 위로 뚫고 올라가면 **골든크로스** → 상승 신호!

        **언제 매수/매도?**
        - 🟢 매수: 단기 이평선이 장기 이평선을 위로 돌파 (골든크로스)
        - 🔴 매도: 단기 이평선이 장기 이평선 아래로 떨어짐 (데드크로스)

        **장점**
        - 큰 상승 추세를 잡아낼 수 있음
        - 이해하기 쉽고 직관적
        - 장기 추세를 따라갈 수 있음

        **단점**
        - 횡보장(옆으로 움직이는 장)에서 잦은 거래로 손실 가능
        - 신호가 늦게 나올 수 있음 (후행 지표)

        **이런 분께 추천**
        추세를 따라가고 싶은 투자자, 큰 상승장을 놓치고 싶지 않은 분
        """)

    # RSI
    with st.expander("📊 RSI (상대강도지수) - 과매수/과매도 전략"):
        st.markdown("""
        **전략 설명**
        RSI는 0~100 사이의 값으로, 주가가 얼마나 과열되었는지 또는 침체되었는지를 나타냅니다.
        70 이상이면 "너무 올랐다" (과매수), 30 이하면 "너무 떨어졌다" (과매도)

        **언제 매수/매도?**
        - 🟢 매수: RSI < 30 (주가가 너무 떨어졌을 때, 곧 반등 예상)
        - 🔴 매도: RSI > 70 (주가가 너무 올랐을 때, 곧 조정 예상)

        **장점**
        - 단기적인 반등/조정을 잡기 좋음
        - 박스권(일정 범위 안에서 움직이는) 장세에 유리
        - 명확한 매매 기준

        **단점**
        - 강한 추세장에서는 오랫동안 과매수/과매도 구간에 머물 수 있음
        - 추세를 거스르는 역발상 전략

        **이런 분께 추천**
        단타/스윙 트레이더, 박스권에서 거래하고 싶은 분
        """)

    # Bollinger Bands
    with st.expander("📉 Bollinger Bands (볼린저 밴드) - 통계적 범위 전략"):
        st.markdown("""
        **전략 설명**
        볼린저 밴드는 이동평균선을 중심으로 위아래로 통계적 범위를 그린 밴드입니다.
        - **상단 밴드**: 통계적으로 "비싼" 가격 (평균 + 2 표준편차)
        - **중간 밴드**: 평균 가격 (이동평균선)
        - **하단 밴드**: 통계적으로 "싼" 가격 (평균 - 2 표준편차)

        가격이 밴드 밖으로 나가면 다시 평균으로 돌아올 것이라고 예상하는 전략!

        **언제 매수/매도?**
        - 🟢 매수: 가격이 하단 밴드에 닿음 (너무 싸다, 곧 올라올 것)
        - 🔴 매도: 가격이 상단 밴드에 닿음 (너무 비싸다, 곧 내려올 것)

        **장점**
        - 변동성을 고려한 매매
        - 평균 회귀 전략에 강함
        - 통계적으로 근거 있는 접근

        **단점**
        - 강한 추세장에서는 밴드를 벗어나 계속 움직일 수 있음
        - 추세를 따라가지 않음

        **이런 분께 추천**
        통계적 접근을 선호하는 투자자, 박스권 매매를 좋아하는 분
        """)

    # MACD
    with st.expander("📈 MACD (이동평균 수렴확산) - 모멘텀 전략"):
        st.markdown("""
        **전략 설명**
        MACD는 단기 이평선(12일)과 장기 이평선(26일)의 차이로, 주가의 "기세"를 측정합니다.
        MACD 선이 Signal 선(9일 이평선)을 뚫고 올라가면 상승 기세가 강해진다는 신호!

        **언제 매수/매도?**
        - 🟢 매수: MACD 선이 Signal 선을 위로 돌파 (상승 모멘텀 강화)
        - 🔴 매도: MACD 선이 Signal 선 아래로 떨어짐 (하락 모멘텀 강화)

        **장점**
        - 추세 전환을 빠르게 포착
        - 골든크로스보다 민감하고 빠름
        - 모멘텀(추진력)을 잘 표현

        **단점**
        - 횡보장에서 잦은 신호로 손실 가능
        - 변동성이 클 수 있음

        **이런 분께 추천**
        모멘텀 투자를 좋아하는 분, 빠른 추세 전환을 잡고 싶은 트레이더
        """)

    st.markdown("---")
    st.markdown("""
    ### 💡 어떤 전략을 선택해야 할까요?

    - **장기 투자자** → 💎 Buy and Hold
    - **상승 추세를 타고 싶다** → 🌟 Golden Cross 또는 📈 MACD
    - **단기 매매, 박스권 장세** → 📊 RSI 또는 📉 Bollinger Bands
    - **초보자** → 💎 Buy and Hold (가장 단순) 또는 🌟 Golden Cross (이해하기 쉬움)

    **팁**: 여러 전략을 백테스트해보고 성과를 비교해보세요! 각 전략의 수익률, MDD, 샤프 지수를 확인하여 자신에게 맞는 전략을 찾으세요.
    """)
