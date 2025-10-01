# Claude Code 작업 컨텍스트

## 프로젝트 개요
**Trading Backtest System** - 트레이딩 전략 백테스트 웹 애플리케이션

- **배포 URL**: https://backtesting-flux.up.railway.app/
- **GitHub**: https://github.com/jeromwolf/Backtesting
- **개발 기간**: 2025-10-01 ~ 2025-10-02
- **개발자**: Kelly (jeromwolf)
- **AI 협업**: Claude Code

---

## 프로젝트 구조

```
TradingBackTester/
├── app/
│   ├── core/
│   │   ├── data_loader.py      # Yahoo Finance API 데이터 로딩
│   │   ├── backtest_engine.py  # 백테스트 실행 엔진
│   │   └── performance.py      # 성과 분석
│   ├── strategies/
│   │   ├── base.py             # TradingStrategy 추상 베이스 클래스
│   │   ├── factory.py          # StrategyFactory (Strategy Pattern)
│   │   ├── buy_and_hold.py     # Buy and Hold 전략
│   │   ├── golden_cross.py     # Golden Cross 전략
│   │   ├── rsi.py              # RSI 전략
│   │   ├── bollinger.py        # Bollinger Bands 전략
│   │   └── macd.py             # MACD 전략
│   └── ui/
│       └── app.py              # Streamlit 웹 UI
├── requirements.txt
├── Procfile                     # Railway 배포 설정
├── railway.toml                 # Railway 설정
├── runtime.txt                  # Python 버전
├── .streamlit/config.toml       # Streamlit 설정
└── README.md
```

---

## 기술 스택

### Backend
- **Python 3.11**
- **pandas**: 데이터 처리
- **yfinance**: Yahoo Finance API (무료, API 키 불필요)

### Frontend
- **Streamlit 1.50.0**: 웹 UI 프레임워크
- **Plotly 6.3.0**: 인터랙티브 차트
- **openpyxl 3.1.5**: Excel 파일 생성

### Deployment
- **Railway**: 자동 배포 (무료 $5 크레딧/월)
- **GitHub**: 소스 코드 관리

---

## 아키텍처

### Strategy Pattern
모든 트레이딩 전략은 `TradingStrategy` 추상 베이스 클래스를 상속받습니다:

```python
class TradingStrategy(ABC):
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        pass
```

### Factory Pattern
`StrategyFactory`가 전략 타입에 따라 적절한 전략 인스턴스를 생성합니다.

```python
strategy = StrategyFactory.create_strategy('golden_cross', {
    'short_ma': 20,
    'long_ma': 60
})
```

---

## 구현된 전략

### 1. Buy and Hold (매수 후 보유)
- **목적**: 벤치마크
- **로직**: 첫 거래일에 전액 매수 후 끝까지 보유
- **파라미터**: 없음

### 2. Golden Cross (골든크로스)
- **목적**: 추세 추종
- **로직**: 단기 이평선이 장기 이평선을 상향 돌파 시 매수
- **파라미터**: `short_ma`, `long_ma`

### 3. RSI (상대강도지수)
- **목적**: 과매수/과매도 포착
- **로직**: RSI < oversold 시 매수, RSI > overbought 시 매도
- **파라미터**: `rsi_period`, `oversold`, `overbought`

### 4. Bollinger Bands (볼린저 밴드)
- **목적**: 평균 회귀
- **로직**: 가격이 하단 밴드 터치 시 매수, 상단 밴드 터치 시 매도
- **파라미터**: `period`, `std_dev`

### 5. MACD (이동평균 수렴확산)
- **목적**: 모멘텀 포착
- **로직**: MACD 선이 Signal 선 상향 돌파 시 매수
- **파라미터**: `fast_period`, `slow_period`, `signal_period`

---

## 성과 지표

- **누적 수익률**: 총 수익률 (%)
- **CAGR**: 연평균 복리 수익률
- **MDD**: 최대 낙폭 (Maximum Drawdown)
- **Sharpe Ratio**: 위험 대비 수익률
- **승률**: 수익 거래 비율 (%)
- **총 거래 횟수**: 매수/매도 쌍의 개수

---

## 주요 기능

### 1. 데이터 로딩
- Yahoo Finance API를 통해 실시간 주식 데이터 다운로드
- 지원 간격: 1분봉, 5분봉, 15분봉, 30분봉, 1시간봉, 일봉
- 종목: 미국 주식 (TSLA, AAPL, GOOGL 등)

### 2. 백테스트 실행
- 신호 생성 → 거래 시뮬레이션 → 성과 분석
- 거래 단위: 전액 또는 고정 금액 ($100, $500, $1000)
- 초기 자본 설정 가능

### 3. 시각화
- Plotly 인터랙티브 차트
- 가격 차트 + 매매 신호 (삼각형 마커)
- 전략별 지표 표시 (이동평균선, RSI 등)
- 누적 수익률 차트

### 4. 데이터 표시
- 최대 1000개 행 표시 (메모리 효율)
- 1000개 초과 시 최근 1000개만 표시 + 경고 메시지
- Excel 다운로드로 전체 데이터 접근

### 5. Excel 다운로드
- 시계열 데이터 (OHLCV, 거래 로그, 수익률 등)
- 성과 종합 (모든 지표)
- 전략별 기술적 지표 포함

---

## 개발 히스토리

### Phase 1: 리팩토링 (완료)
- 단일 파일 `backtester.py` → 모듈형 구조
- Strategy Pattern 도입
- 100% 결과 일치 검증

### Phase 2: 전략 추가 (완료)
- RSI 전략 구현
- Bollinger Bands 전략 구현
- MACD 전략 구현
- Buy and Hold 전략 추가 (벤치마크)

### Phase 3: Streamlit UI (완료)
- 전략 선택 및 파라미터 입력
- 인터랙티브 차트 (Plotly)
- Excel 다운로드
- 초보자를 위한 상세 전략 설명

### Phase 4: 배포 (완료)
- Streamlit Cloud 시도 (접근 권한 이슈)
- Railway로 마이그레이션 성공
- 도메인: https://backtesting-flux.up.railway.app/
- 자동 배포 (GitHub push → Railway 재배포)

### Phase 5: 최적화 (완료)
- 메모리 효율적 데이터 표시 (최대 1000개)
- UI 단순화 (슬라이더/라디오 버튼 제거)
- 페이지 초기화 문제 해결

---

## 주요 이슈 및 해결

### 1. Buy and Hold 신호 생성 오류
**문제**: 모든 trade_signal이 1로 설정되어 매수 신호가 발생하지 않음
**해결**: 첫 날 signal=0, 두 번째 날부터 signal=1로 설정하여 0→1 변화 생성

### 2. Streamlit Cloud 배포 실패
**문제**: "You do not have access to this app" 에러
**원인**: 계정 연동 또는 권한 문제
**해결**: Railway로 마이그레이션

### 3. 시계열 데이터 페이지 초기화
**문제**: 슬라이더/라디오 버튼 클릭 시 백테스트 결과가 사라짐
**원인**: Streamlit의 재실행 메커니즘 + session_state 미사용
**해결**: 위젯 제거, 자동으로 최대 1000개만 표시

### 4. 메모리 효율
**문제**: 1분봉 데이터 (~350,000개 행) 처리 시 메모리 부족 가능
**해결**: 화면 표시는 최대 1000개, Excel 다운로드로 전체 데이터 제공

---

## 배포 설정

### Railway 자동 배포
1. GitHub에 push
2. Railway가 변경사항 감지
3. 자동 빌드 및 배포 (1-2분)

### 필요한 파일
- `requirements.txt`: Python 패키지
- `Procfile`: 실행 명령어
- `railway.toml`: Railway 설정
- `runtime.txt`: Python 버전

---

## 다음 버전 계획 (V2)

### 제안된 기능
1. **다중 전략 비교**
   - 여러 전략을 동시에 실행하여 성과 비교
   - 전략별 수익률 차트 오버레이

2. **포트폴리오 백테스트**
   - 여러 종목 동시 백테스트
   - 포트폴리오 수익률 계산

3. **파라미터 최적화**
   - Grid Search로 최적 파라미터 탐색
   - 백테스트 결과에 따른 자동 파라미터 추천

4. **추가 기술적 지표**
   - Stochastic Oscillator
   - ATR (Average True Range)
   - Ichimoku Cloud

5. **백테스트 설정 고도화**
   - 거래 수수료 반영
   - 슬리피지 (Slippage) 반영
   - 레버리지 설정

6. **알림 기능**
   - 실시간 신호 알림
   - 이메일/SMS 통보

7. **성과 분석 강화**
   - 월별/연도별 수익률 분해
   - 드로다운 차트
   - 거래 분석 (평균 보유 기간, 승/패 거래 분포 등)

---

## 참고 자료

### 문서
- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [yfinance 문서](https://pypi.org/project/yfinance/)
- [Railway 문서](https://docs.railway.app/)

### 전략 참고
- [Golden Cross 전략](https://www.investopedia.com/terms/g/goldencross.asp)
- [RSI 지표](https://www.investopedia.com/terms/r/rsi.asp)
- [Bollinger Bands](https://www.investopedia.com/terms/b/bollingerbands.asp)
- [MACD 지표](https://www.investopedia.com/terms/m/macd.asp)

---

## 협업 노트

### Kelly의 요구사항
- 주식 초보자도 이해할 수 있는 UI
- 전략별 상세 설명
- 무료 배포 솔루션
- 메모리 효율적인 데이터 처리

### Claude Code의 역할
- 아키텍처 설계 (Strategy Pattern)
- 코드 구현 및 리팩토링
- 배포 설정 및 트러블슈팅
- 문서화

---

## 마지막 업데이트
**날짜**: 2025-10-02
**버전**: v1.0
**상태**: 배포 완료
**다음 작업**: v2.0 기획
