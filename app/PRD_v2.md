# 시스템 트레이딩 백테스트 PRD v2.0

***

## 1. 제품 개요

- **프로젝트명**: Multi-Strategy Trading Backtest System
- **목표**:
  - 다양한 트레이딩 전략을 백테스트하고 비교 분석할 수 있는 시스템
  - Streamlit 기반 웹 UI로 전략 설정 및 결과 시각화
  - Streamlit Community Cloud 배포로 언제 어디서나 접근 가능

## 2. 사용자 및 범위

- **주요 사용자**:
  - 코딩을 통해 투자 전략을 검증하고 싶은 개인 투자자
  - 여러 전략을 비교하고 최적의 전략을 찾고자 하는 트레이더

- **Phase 1 범위 (MVP)**:
  - Strategy Pattern 기반 아키텍처 리팩토링
  - Golden Cross 전략 구현 (기존 로직 유지)
  - 모듈화된 구조로 전환
  - 기존 기능 동작 보장

## 3. 핵심 기능

### 3.1 전략 시스템
- **Strategy Pattern**: 전략 추가/교체 용이한 구조
- **지원 전략** (단계별 확장):
  - Phase 1: Golden Cross (20/60 이동평균)
  - Phase 2: RSI 전략
  - Phase 2: Bollinger Bands 전략
  - Phase 2: MACD 전략

### 3.2 데이터 처리
- yfinance를 통한 실시간 데이터 수집 (무료, API 키 불필요)
- 다양한 시간 단위 지원 (1분, 5분, 1시간, 1일)
- MultiIndex 데이터 자동 정규화

### 3.3 백테스트 엔진
- 전략 독립적인 거래 시뮬레이션
- 매수/매도 로직 (종가 기준)
- 포지션 관리 및 자산 추적
- 거래 단위 설정 (고정 금액 or Full)

### 3.4 성과 분석
- 핵심 지표: 누적 수익률, MDD, 승률, CAGR, Sharpe Ratio
- 시계열 데이터: 가격, 지표, 신호, 포지션, 자산
- 멀티 전략 비교 테이블 (Phase 4)

### 3.5 UI/UX (Phase 3+)
- Streamlit 웹 인터페이스
- 전략 선택 및 파라미터 입력 폼
- 실시간 결과 시각화 (차트, 테이블)
- Excel 파일 다운로드

### 3.6 배포 (Phase 6)
- Streamlit Community Cloud 무료 배포
- GitHub 연동 자동 배포

## 4. 기술 스택

### 4.1 Backend
- **언어**: Python 3.9+
- **데이터 수집**: yfinance (무료)
- **데이터 처리**: Pandas, NumPy
- **지표 계산**: Pandas TA (선택)
- **Excel 출력**: openpyxl

### 4.2 Frontend
- **UI Framework**: Streamlit
- **차트**: Plotly (인터랙티브), Streamlit native charts
- **배포**: Streamlit Community Cloud

### 4.3 아키텍처 패턴
- **Strategy Pattern**: 전략 캡슐화
- **Factory Pattern**: 전략 생성
- **모듈 분리**: core, strategies, ui, utils

## 5. 프로젝트 구조

```
TradingBackTester/
├── app/
│   ├── strategies/              # 전략 모듈
│   │   ├── __init__.py
│   │   ├── base.py             # TradingStrategy 추상 클래스
│   │   ├── golden_cross.py     # Golden Cross 전략
│   │   ├── rsi.py              # RSI 전략 (Phase 2)
│   │   ├── bollinger.py        # Bollinger Bands (Phase 2)
│   │   ├── macd.py             # MACD 전략 (Phase 2)
│   │   └── factory.py          # Strategy Factory
│   │
│   ├── core/                    # 핵심 로직
│   │   ├── __init__.py
│   │   ├── data_loader.py      # 데이터 수집 (yfinance)
│   │   ├── backtest_engine.py  # 백테스트 엔진
│   │   └── performance.py      # 성과 계산
│   │
│   ├── ui/                      # Streamlit UI (Phase 3)
│   │   ├── app.py              # 메인 앱
│   │   └── components/         # UI 컴포넌트
│   │
│   ├── utils/                   # 유틸리티
│   │   ├── __init__.py
│   │   ├── config.py           # Config 관리
│   │   └── excel_export.py     # Excel 출력
│   │
│   ├── config.yml              # 설정 파일
│   ├── backtester.py           # 기존 파일 (Phase 1에서 리팩토링)
│   ├── PRD.md                  # 원본 PRD
│   ├── PRD_v2.md               # 이 문서
│   └── requirements.txt
│
├── .streamlit/
│   └── config.toml             # Streamlit 설정
├── .gitignore
└── README.md
```

## 6. Config 구조

### Phase 1 (현재 유지)
```yaml
strategy:
  ticker: 'TSLA'
  short_ma: 20
  long_ma: 60
  start_date: '2024-01-01'
  end_date: '2025-10-01'
  initial_capital: 1000
  trade_unit_size: full
  time_period: '1d'
```

### Phase 2+ (멀티 전략)
```yaml
strategies:
  - name: "Golden Cross TSLA"
    type: "golden_cross"
    ticker: "TSLA"
    params:
      short_ma: 20
      long_ma: 60

  - name: "RSI AAPL"
    type: "rsi"
    ticker: "AAPL"
    params:
      rsi_period: 14
      oversold: 30
      overbought: 70

backtest:
  start_date: '2024-01-01'
  end_date: '2025-10-01'
  initial_capital: 1000
  trade_unit_size: full
  time_period: '1d'
```

## 7. Phase별 구현 계획

### Phase 1: 기반 구조 리팩토링 (1-2일) ⭐⭐⭐
**목표**: 모듈화 및 Strategy Pattern 적용

**세부 태스크**:
- [ ] 폴더 구조 생성 (strategies/, core/, utils/)
- [ ] Base Strategy 추상 클래스 작성
- [ ] Data Loader 모듈 분리
- [ ] Backtest Engine 모듈 분리
- [ ] Performance 모듈 분리
- [ ] Golden Cross Strategy 클래스 구현
- [ ] Strategy Factory 구현
- [ ] 통합 테스트 (기존 config.yml로 동작 확인)

### Phase 2: 추가 전략 구현 (2-3일) ⭐⭐⭐
**목표**: RSI, Bollinger Bands 전략 추가

**세부 태스크**:
- [ ] RSI 전략 클래스 구현
- [ ] Bollinger Bands 전략 클래스 구현
- [ ] MACD 전략 클래스 구현 (선택)
- [ ] 각 전략별 테스트
- [ ] Config 멀티 전략 지원 확장

### Phase 3: Streamlit UI 기본 (2-3일) ⭐⭐⭐
**목표**: 웹 UI로 단일 전략 실행

**세부 태스크**:
- [ ] Streamlit 앱 기본 구조
- [ ] 전략 선택 사이드바
- [ ] 파라미터 입력 폼
- [ ] 백테스트 실행 버튼
- [ ] 성과 지표 표시 (st.metric)
- [ ] 데이터 테이블 표시
- [ ] 가격 차트 표시
- [ ] Excel 다운로드 버튼

### Phase 4: 멀티 전략 비교 (2-3일) ⭐⭐
**목표**: 여러 전략 동시 실행 및 비교

**세부 태스크**:
- [ ] 멀티 전략 선택 UI
- [ ] 병렬 백테스트 실행
- [ ] 전략 비교 테이블
- [ ] 전략별 누적 수익률 차트
- [ ] 성과 지표 비교 차트

### Phase 5: 고급 기능 (3-4일) ⭐ (선택)
**목표**: 차트 고도화, 최적화

**세부 태스크**:
- [ ] Plotly 인터랙티브 차트
- [ ] 매매 신호 마커 표시
- [ ] 파라미터 최적화 (Grid Search)
- [ ] 캐싱 최적화

### Phase 6: 배포 (1일) ⭐⭐⭐
**목표**: Streamlit Cloud 배포

**세부 태스크**:
- [ ] GitHub repository 설정
- [ ] .gitignore 설정
- [ ] requirements.txt 최종 확인
- [ ] Streamlit Cloud 연결
- [ ] 배포 테스트

## 8. 성공 기준

### Phase 1 (MVP)
- ✅ 리팩토링 후에도 기존 기능 100% 동작
- ✅ 새로운 전략 추가가 용이한 구조
- ✅ 모듈 간 의존성 최소화

### Phase 3 (UI)
- ✅ 브라우저에서 전략 실행 가능
- ✅ 결과를 시각적으로 확인 가능
- ✅ Excel 다운로드 정상 작동

### Phase 6 (배포)
- ✅ 인터넷 어디서나 접속 가능
- ✅ 무료 호스팅 (비용 0원)

## 9. 제약사항 및 가정

- 거래 수수료/슬리피지 미고려 (MVP)
- yfinance 데이터 정확성 가정
- Streamlit Community Cloud 무료 티어 제한 (sleep mode)
- 실시간 트레이딩 아님 (백테스트 전용)

## 10. 향후 확장 가능성

- 실시간 데이터 모니터링
- 알림 시스템 (이메일, Slack)
- 포트폴리오 최적화
- 다중 종목 동시 백테스트
- 머신러닝 기반 전략
- 데이터베이스 연동 (히스토리 저장)
