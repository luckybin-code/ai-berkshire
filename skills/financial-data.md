# 재무 데이터 수집 및 교차 검증 규정

이 규정은 기업 재무 데이터가 관련된 모든 리서치에 적용된다. **모든 핵심 데이터는 반드시 두 개의 독립된 출처에서 확보해야 하며, 오차가 1%를 초과하면 반드시 표시한다.**

---

## 데이터 출처 우선순위

### 미국 주식 (PDD, 텐센트 ADR, 넷이즈 ADR 등)

| 우선순위 | 출처 | URL | 접근 방식 |
|--------|------|-----|---------|
| 1 (주) | **macrotrends** | macrotrends.net/stocks/charts/{ticker} | 직접 접속, 가입 불필요 |
| 2 (부) | **stockanalysis** | stockanalysis.com/stocks/{ticker}/financials | 직접 접속, 가입 불필요 |
| 원본 1차 자료 | SEC EDGAR | sec.gov/cgi-bin/browse-edgar | 10-K / 10-Q 원문 |

### 홍콩 주식 (텐센트 0700, 넷이즈 9999, 메이퇀 3690 등)

| 우선순위 | 출처 | URL | 접근 방식 |
|--------|------|-----|---------|
| 1 (주) | **aastocks** | aastocks.com/tc/stocks/analysis/company-fundamental | 직접 접속 |
| 2 (부) | **macrotrends** (ADR 코드) | 텐센트는 TCEHY, 넷이즈는 NTES | 직접 접속 |
| 원본 1차 자료 | HKEX 披露易 | hkexnews.hk | 연차보고서 PDF |

### 중국 A주 (37호유, 지비트 등)

| 우선순위 | 출처 | URL | 접근 방식 |
|--------|------|-----|---------|
| 1 (주) | **동방재부(东方财富)** | eastmoney.com → 종목 코드 검색 → 재무제표 | 직접 접속 |
| 2 (부) | **거차오자쉰(巨潮资讯)** | cninfo.com.cn | 원본 연차/분기 보고서 PDF |

### 한국 주식 (삼성전자, SK하이닉스 등)

| 우선순위 | 출처 | 접근 방식 |
|--------|------|---------|
| 1 (주) | **`tools/kr_data.py`** (네이버금융 실시간 시세/밸류에이션) | `python3 tools/kr_data.py quote {종목코드}`, `valuation {종목코드}`, `search {회사명}` — 인증 불필요, 즉시 사용 가능 |
| 2 (부) | **DART 전자공시시스템(dart.fss.or.kr)** | `python3 tools/kr_data.py financials {종목코드} --year {연도} --report {annual\|q1\|half\|q3}` — 무료 인증키 필요(최초 1회 `setup` 실행), 사업/분기보고서 원문 조회는 dart.fss.or.kr에서 직접 |
| 원본 1차 자료 | **KRX정보데이터시스템** | data.krx.co.kr — 공식 시세/지수/투자자별 매매동향 |
| 보조 | **네이버페이 증권** | finance.naver.com/item/main.naver?code={종목코드} — 컨센서스, 동종업계 비교, 뉴스 |
| 보조 | **한경컨센서스** | consensus.hankyung.com — 증권사 리포트 원문(목표주가, 투자의견) |

한국 주식은 `tools/kr_data.py`가 1차 데이터 소스다. `quote`/`valuation`/`search`는 즉시 쓸 수 있고, `financials`는 DART Open API 인증키(무료, opendart.fss.or.kr에서 발급)가 있어야 한다. 인증키가 없거나 DART 조회가 실패하면 WebSearch로 dart.fss.or.kr 원문 공시를 직접 찾아 보완한다.

---

## 실행 규정

### 1단계: 데이터 수집

각 재무 지표(매출, 순이익, 매출총이익률, 영업현금흐름, 부채비율 등)에 대해 **출처1**과 **출처2**에서 각각 수치를 확보한다.

### 2단계: 오차 계산 및 표시

```
오차율 = |출처1 수치 - 출처2 수치| / 출처1 수치 × 100%
```

| 오차 | 처리 방식 |
|------|---------|
| ≤ 1% | ✅ 일치, 출처1 수치를 채택하고 두 출처를 모두 표기 |
| 1% ~ 5% | ⚠️ "데이터 차이 존재"로 표시, 두 수치를 병기하고 가능한 원인(환율/회계 기준) 설명 |
| > 5% | ❌ "데이터에 중대한 차이 존재"로 표시, 반드시 원본 재무제표를 확인해야 하며 그대로 사용해서는 안 됨 |

### 3단계: 데이터 표기 형식

각 핵심 데이터는 다음 형식으로 표기한다:

```
매출: 1,239억 위안 ✅
  - macrotrends: 1,241억 위안
  - stockanalysis: 1,237억 위안
  - 오차: 0.3%
```

차이 발생 예시:
```
순이익: 245억 위안 ⚠️ 데이터 차이 존재
  - macrotrends: 245억 위안 (GAAP)
  - stockanalysis: 278억 위안 (Non-GAAP)
  - 오차: 13.5% — 원인: 회계 기준 차이 (GAAP vs Non-GAAP)
```

---

## 흔한 차이 원인 (반드시 데이터 오류는 아님)

| 원인 | 설명 |
|------|------|
| GAAP vs Non-GAAP | 가장 흔한 경우, 특히 이익 관련 데이터 |
| 환율 환산 | 홍콩달러/위안/달러 환산 시점 차이 |
| 회계연도 정의 | 자연년 vs 회계연도 (예: 애플의 회계연도는 10월에 종료) |
| 연결 기준 | 소수주주지분 포함 여부 |
| 데이터 업데이트 지연 | 특정 플랫폼이 최신 분기 보고서를 아직 반영하지 않음 |

---

## 특별 규칙

1. **비상장 기업** (미호요, 릴리스 등): 1차 출처만 있을 경우, 데이터 앞에 `[추정]`을 표시하고 교차 검증은 수행하지 않는다
2. **분기 데이터 vs 연간 데이터**: 교차 검증은 연간 데이터를 우선 사용하며, 분기 데이터는 일부 출처에서 업데이트가 지연될 수 있다
3. **원본 재무제표 우선**: 두 출처 모두 원본 재무제표(10-K/연차보고서 PDF)와 불일치할 경우, 원본 재무제표를 기준으로 삼고 출처 오류를 표시한다

---

## 빠른 색인

| 시나리오 | 주요 출처 | 보조 출처 |
|------|---------|---------|
| PDD / 핀둬둬 | macrotrends.net/stocks/charts/PDD | stockanalysis.com/stocks/pdd |
| 텐센트 | macrotrends.net/stocks/charts/TCEHY | aastocks (0700.HK) |
| 넷이즈 | macrotrends.net/stocks/charts/NTES | aastocks (9999.HK) |
| 37호유 | eastmoney.com (002555) | cninfo.com.cn |
| 지비트 | eastmoney.com (603444) | cninfo.com.cn |
| Nintendo | macrotrends.net/stocks/charts/NTDOY | stockanalysis.com/stocks/ntdoy |
| Capcom | macrotrends (CCOEY) | stockanalysis (CCOEY) |
| 삼성전자 | `python3 tools/kr_data.py valuation 005930` | dart.fss.or.kr (종목코드 005930) |
| SK하이닉스 | `python3 tools/kr_data.py valuation 000660` | dart.fss.or.kr (종목코드 000660) |
