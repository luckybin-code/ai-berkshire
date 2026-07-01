# AI Berkshire — 프로젝트 지침

## 프로젝트 개요

Claude Code 기반 가치투자 리서치 Skill 모음. 4대 거장 프레임워크: 버핏, 멍거, 돤융핑, 리루.
GitHub: xbtlin/ai-berkshire (fork: luckybin-code/ai-berkshire)

## 프로젝트 구조

```
skills/          — 투자 리서치 Skill 정의(.md), ~/.claude/commands/ 로 복사해서 사용
tools/           — 보조 도구 (financial_rigor.py 정밀 계산)
reports/         — 투자 리서치 보고서 출력
assets/          — 이미지 등 정적 자산
```

## 보고서 디렉토리 구조

모든 보고서는 **회사명**으로 폴더를 만들고, 해당 회사 관련 모든 보고서를 그 폴더 안에 둡니다:

```
reports/
├── AI산업연구/               — AI 산업체인 전체 조망 연구 (상단 고정)
│   ├── AI-오층케이크-산업전체조망연구-20260605.md
│   └── AI-오층케이크-공식계정용-20260605.md
├── 텐센트/                   — 텐센트 관련 모든 리서치 보고서
│   ├── 텐센트-research-20260408.md
│   ├── 텐센트-earnings-2025Q4.md
│   ├── 텐센트-management-20260409.md
│   └── 텐센트-thesis.md
├── 핀둬둬/                   — 핀둬둬 관련 모든 리서치 보고서
├── 팝마트/                   — 팝마트 관련 모든 리서치 보고서
├── 원자력발전-industry-20260409.md  — 산업 보고서는 루트 디렉토리
├── AI연산력-funnel-20260509.md      — 깔때기(퍼널) 스크리닝 보고서는 루트 디렉토리
├── AI-로테이션판단-20260509.md       — 테마 단위 종합 판단 보고서는 루트 디렉토리
├── portfolio-latest.md             — 포트폴리오 보고서는 루트 디렉토리
└── 다중기업비교-checklist-20260408.md — 여러 기업 비교 보고서는 루트 디렉토리
```

## 보고서 파일명 규칙

| Skill | 파일명 형식 | 예시 |
|------|---------|------|
| /investment-team | `{회사명}/` 디렉토리 안에 4개 관점 + 최종 보고서 | `reports/핀둬둬/최종보고서.md` |
| /investment-research | `{회사명}-research-{YYYYMMDD}.md` | `reports/텐센트/텐센트-research-20260408.md` |
| /investment-checklist | `{회사명}-checklist-{YYYYMMDD}.md` | `reports/텐센트/텐센트-checklist-20260408.md` |
| /industry-research | `{산업명}-industry-{YYYYMMDD}.md` (루트 디렉토리) | `reports/원자력발전-industry-20260409.md` |
| /industry-funnel | `{산업명}-funnel-{YYYYMMDD}.md` (루트 디렉토리) | `reports/AI연산력-funnel-20260509.md` |
| /private-company-research | `{회사명}-private-{YYYYMMDD}.md` | `reports/바이트댄스/바이트댄스-private-20260408.md` |
| /earnings-review | `{회사명}-earnings-{기간}.md` | `reports/텐센트/텐센트-earnings-2025Q4.md` |
| /earnings-team | `{회사명}/` 디렉토리 안에 4개 거장 관점 + 리서치 초고 + 공식계정 원고 + 독자 리뷰 | `reports/텐센트/텐센트-earnings-2025Q4.md` (공식계정 확정본) |
| /thesis-tracker | `{회사명}-thesis.md` (장기 유지관리) | `reports/텐센트/텐센트-thesis.md` |
| /portfolio-review | `portfolio-latest.md` (루트 디렉토리, 지속 업데이트) | `reports/portfolio-latest.md` |
| /management-deep-dive | `{회사명}-management-{YYYYMMDD}.md` | `reports/텐센트/텐센트-management-20260409.md` |

## /investment-team 파일 구조

```
reports/{회사명}/
├── README.md                          — 리서치 프레임워크 개요 + 핵심 결론
├── 01-비즈니스모델분석-돤융핑관점.md
├── 02-재무밸류에이션분석-버핏관점.md
├── 03-산업경쟁분석-멍거관점.md
├── 04-리스크경영진평가-리루관점.md
└── 최종보고서.md                       — 팀 리드 종합 보고서
```

## 투자 리서치 핵심 원칙 (최우선순위)

- **객관, 객관, 객관** — 모든 투자 리서치 분석은 사실과 데이터에 근거해야 하며, 주관적 억측을 엄격히 금지
- **"사실"과 "의견"을 엄격히 구분**: 사실은 데이터로 뒷받침하고, 의견은 반드시 "의견" 또는 "추측"으로 명시
- **입장을 미리 정하지 않음**: 강세/약세를 미리 정하지 않고, 먼저 데이터를 제시하고, 논리를 전개한 뒤, 마지막에 결론을 낸다. 결론은 데이터에서 자연스럽게 도출되어야 함
- "제 생각에는", "제가 보기엔", "명백히" 같은 주관적 표현 금지 — "데이터에 따르면", "증거가 보여주듯", "OO 출처에 따르면"으로 대체
- **양면을 모두 제시**: 모든 핵심 판단에는 반드시 반대 근거("하지만 다른 한편으로는...")를 함께 제시하여, 독자가 스스로 판단할 수 있게 함
- 불확실한 사안은 "불확실함" 또는 "데이터 부족"이라고 솔직히 말할 것 — 추측으로 확실함을 채우지 말 것
- 모든 skill(investment-team, investment-research, earnings-review 등)은 실행 시 위 원칙을 반드시 준수해야 함

## 보고서 언어와 스타일

- 모든 보고서는 **한국어**로 작성
- 스타일: 직접적이고 날카롭게, 군더더기 없이
- 데이터는 반드시 출처를 명시하고, 핵심 데이터는 최소 2개 출처로 교차검증
- 추정치는 반드시 "추정"이라고 표기
- 평점은 ★ 기호 사용(★1~5), 반쪽 별은 사용하지 않음
- 버핏/멍거/돤융핑/리루의 어록을 곳곳에 인용하며 코멘트

## GitHub 작업

- 로컬 클론 경로: `d:\claude code\ai-berkshire\`
- 원격 저장소(fork): `https://github.com/luckybin-code/ai-berkshire.git`
- 원본 저장소(upstream): `https://github.com/xbtlin/ai-berkshire.git`
- 푸시 전에 먼저 `git pull --rebase origin main` (원격에 새 커밋이 자주 생김)
- commit message는 한국어로, 무엇을 바꿨는지 명확하게 서술
- 중간 과정 파일(예: data_collection.md)은 푸시하지 않고, 최종 보고서만 푸시

## 자주 쓰는 명령어

```bash
# 보고서를 GitHub에 푸시
cd "d:\claude code\ai-berkshire"
git add reports/xxx.md
git commit -m "xxx 보고서 추가"
git pull --rebase origin main
git push origin main
```

## 주의사항

- 시가총액은 반드시 손으로 검산: 주가 × 총 발행주식수, 보고서상 시가총액과 대조
- 통화 단위를 명확히 할 것(홍콩달러/위안/달러 등), 혼동 방지
- PE/ROE 등 지표는 `tools/financial_rigor.py`로 정밀 계산
- 보고서 작성 완료 후 GitHub에 푸시할지 먼저 물어볼 것
