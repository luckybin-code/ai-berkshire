#!/usr/bin/env python3
"""한국 주식 데이터 도구 — 네이버금융 시세/밸류에이션 + DART Open API 재무제표. 외부 의존성 없음(stdlib만 사용).

Claude Code Skill에 한국 주식의 실시간 시세, 밸류에이션 지표, 재무제표 데이터를 제공한다.
설계 원칙: 독립 모듈, 기존 도구(ashare_data.py 등)에 영향 없음; curl 직접 연결로 시스템 프록시 우회.

사용법 (Skill이 자동으로 호출):
    python3 tools/kr_data.py quote 005930                       # 실시간 시세
    python3 tools/kr_data.py valuation 005930                   # 밸류에이션 지표 (PER/PBR/EPS/BPS 등)
    python3 tools/kr_data.py search 삼성전자                     # 종목코드 검색
    python3 tools/kr_data.py setup                              # DART 기업코드 매핑 캐시 생성 (최초 1회, API 키 필요)
    python3 tools/kr_data.py financials 005930 --year 2025 --report annual   # 재무제표 (DART, API 키 필요)

quote/valuation/search는 네이버금융 공개 API를 사용하며 별도 인증이 필요 없다.
financials(재무제표)는 금융감독원 DART Open API를 사용하며, 무료 인증키가 필요하다:

    1. https://opendart.fss.or.kr 접속 후 회원가입
    2. "인증키 신청/관리" 메뉴에서 오픈API 이용자 등록 (즉시 발급, 무료)
    3. 발급받은 인증키를 환경변수로 등록:
         export DART_API_KEY="발급받은키"
       또는 이 프로젝트 루트에 .env 파일을 만들고 다음 줄 추가:
         DART_API_KEY=발급받은키
    4. 최초 1회 `python3 tools/kr_data.py setup` 실행 (전체 상장기업 코드 매핑 다운로드/캐시)

Python >= 3.8 필요, 외부 의존성 없음(표준 라이브러리만 사용).
"""

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import quote as urlquote
from urllib.parse import urlencode

_TIMEOUT = 15
_ROOT = Path(__file__).resolve().parent.parent
_CORP_CODE_CACHE = _ROOT / "data" / "dart_corp_codes.json"

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

# curl 경로는 OS/셸마다 다르다 (macOS/Linux: /usr/bin/curl, Git Bash: /mingw64/bin/curl,
# 네이티브 Windows Python: curl.exe). 하드코딩하지 않고 PATH에서 찾는다.
_CURL = shutil.which("curl")


def _curl_bytes(url: str) -> bytes:
    """curl --noproxy 직접 연결로 원본 바이트를 가져온다 (ZIP 등 바이너리 응답용)."""
    if not _CURL:
        raise FileNotFoundError(
            "curl 실행 파일을 PATH에서 찾을 수 없습니다. "
            "Windows 10/11에는 기본 내장되어 있으니 새 터미널에서 다시 시도하거나 curl 설치를 확인하세요."
        )
    result = subprocess.run(
        [_CURL, "-s", "--noproxy", "*", "-H", f"User-Agent: {_UA}", url],
        capture_output=True, timeout=_TIMEOUT,
    )
    if result.returncode != 0:
        raise ConnectionError(f"요청 실패: {url}")
    return result.stdout


def _curl_text(url: str) -> str:
    raw = _curl_bytes(url)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("euc-kr", errors="replace")


def _curl_json(url: str, params: dict | None = None):
    if params:
        url = f"{url}?{urlencode(params)}"
    text = _curl_text(url)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ConnectionError(f"JSON 파싱 실패 — 응답: {text[:300]}")


def _dart_key() -> str | None:
    key = os.environ.get("DART_API_KEY")
    if key:
        return key.strip()
    env_file = _ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("DART_API_KEY"):
                _, _, value = line.partition("=")
                return value.strip().strip('"').strip("'")
    return None


def _no_key_message():
    print("❌ DART_API_KEY가 설정되어 있지 않습니다.")
    print("   1) https://opendart.fss.or.kr 에서 무료로 인증키를 발급받으세요.")
    print("   2) export DART_API_KEY=\"발급받은키\"  (또는 .env 파일에 DART_API_KEY=발급받은키 추가)")


def _clean_code(code: str) -> str:
    digits = re.sub(r"[^0-9]", "", code.strip())
    return digits.zfill(6)[:6] if digits else code.strip()


# ---------------------------------------------------------------------------
# 네이버금융 실시간 시세 / 밸류에이션 / 검색 (인증 불필요)
# ---------------------------------------------------------------------------

def cmd_quote(code: str):
    code = _clean_code(code)
    data = _curl_json(f"https://polling.finance.naver.com/api/realtime/domestic/stock/{code}")
    items = data.get("datas", [])
    if not items:
        print(f"❌ 종목 {code}를 찾을 수 없습니다")
        return
    d = items[0]
    exch = d.get("stockExchangeType", {}) or {}

    print("=" * 60)
    print(f"실시간 시세: {d.get('stockName')} ({d.get('itemCode')})")
    print("=" * 60)
    print(f"  현재가:     {d.get('closePrice')}원")
    print(f"  전일대비:   {d.get('compareToPreviousClosePrice')}  ({d.get('fluctuationsRatio')}%)")
    print(f"  시가:       {d.get('openPrice')}원")
    print(f"  고가:       {d.get('highPrice')}원")
    print(f"  저가:       {d.get('lowPrice')}원")
    print(f"  거래량:     {d.get('accumulatedTradingVolume')}주")
    print(f"  거래대금:   {d.get('accumulatedTradingValue')}")
    if d.get("marketValueFull"):
        print(f"  시가총액:   {d.get('marketValueFull')}원")
    print(f"  시장:       {exch.get('name', '-')}")
    print(f"  장상태:     {d.get('marketStatus', '-')}  (기준시각: {d.get('localTradedAt', '-')})")


def cmd_valuation(code: str):
    code = _clean_code(code)
    text = _curl_text(f"https://m.stock.naver.com/api/stock/{code}/integration")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print(f"❌ 종목 {code} 데이터를 가져오지 못했습니다")
        return

    stock_name = data.get("stockName") or (data.get("stockInfo") or {}).get("stockName") or code
    infos = data.get("totalInfos", []) or []
    lookup = {item.get("code"): item for item in infos}

    print("=" * 60)
    print(f"밸류에이션 지표: {stock_name} ({code})")
    print("=" * 60)

    def show(key: str, label: str):
        item = lookup.get(key)
        if not item:
            return
        desc = f" (기준: {item['valueDesc']})" if item.get("valueDesc") else ""
        print(f"  {label:10s}{item.get('value')}{desc}")

    show("marketValue", "시가총액")
    show("per", "PER")
    show("eps", "EPS")
    show("cnsPer", "추정PER")
    show("cnsEps", "추정EPS")
    show("pbr", "PBR")
    show("bps", "BPS")
    show("dividendYieldRatio", "배당수익률")
    show("dividend", "주당배당금")
    show("highPriceOf52Weeks", "52주 최고")
    show("lowPriceOf52Weeks", "52주 최저")
    show("foreignRate", "외인소진율")

    if not infos:
        print("  ⚠️ 밸류에이션 데이터를 찾지 못했습니다 — WebSearch로 보완하세요")

    print("\n  ⚠️ 시가총액·주식수는 반드시 financial_rigor.py verify-market-cap 으로 재검산할 것")


def cmd_search(keyword: str):
    q = urlquote(keyword)
    data = _curl_json(f"https://ac.stock.naver.com/ac?q={q}&target=stock,ipo")
    items = data.get("items", []) or []
    if not items:
        print(f"❌ '{keyword}'와 일치하는 종목을 찾을 수 없습니다")
        return
    print("=" * 60)
    print(f"검색 결과: '{keyword}'")
    print("=" * 60)
    for it in items[:15]:
        print(f"  {it.get('code')}  {it.get('name')}  [{it.get('typeName', '-')}]")


# ---------------------------------------------------------------------------
# DART Open API 재무제표 (무료 인증키 필요)
# ---------------------------------------------------------------------------

_REPORT_CODES = {
    "annual": "11011",  # 사업보고서(연간)
    "q1": "11013",      # 1분기보고서
    "half": "11012",    # 반기보고서
    "q3": "11014",      # 3분기보고서
}

# DART account_nm(계정명)은 기업마다 표기가 조금씩 다를 수 있어 후보를 여러 개 둔다
_ACCOUNT_LABELS = {
    "매출액": "매출액", "수익(매출액)": "매출액", "영업수익": "매출액",
    "영업이익": "영업이익", "영업이익(손실)": "영업이익",
    "당기순이익": "당기순이익", "당기순이익(손실)": "당기순이익",
    "자산총계": "자산총계",
    "부채총계": "부채총계",
    "자본총계": "자본총계",
}


def _load_corp_codes() -> dict | None:
    if not _CORP_CODE_CACHE.exists():
        return None
    return json.loads(_CORP_CODE_CACHE.read_text(encoding="utf-8"))


def cmd_setup():
    key = _dart_key()
    if not key:
        _no_key_message()
        sys.exit(1)

    print("DART 기업코드 매핑 다운로드 중... (전체 상장/비상장 기업 목록, 최초 1회만 필요)")
    raw = _curl_bytes(f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={key}")

    try:
        zf = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        print(f"❌ 다운로드 실패 — 응답 내용: {raw[:300]!r}")
        print("   인증키가 올바른지, 발급 후 활성화까지 시간이 걸리지 않았는지 확인하세요.")
        sys.exit(1)

    xml_bytes = zf.read(zf.namelist()[0])
    root = ET.fromstring(xml_bytes)

    mapping = {}
    for item in root.findall("list"):
        stock_code = (item.findtext("stock_code") or "").strip()
        if not stock_code:
            continue  # 비상장 기업은 종목코드가 없어 제외
        mapping[stock_code] = {
            "corp_code": item.findtext("corp_code"),
            "corp_name": item.findtext("corp_name"),
            "corp_eng_name": item.findtext("corp_eng_name") or "",
        }

    _CORP_CODE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    _CORP_CODE_CACHE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {len(mapping)}개 상장기업 코드 매핑 저장 완료 → {_CORP_CODE_CACHE}")


def cmd_financials(code: str, year: str, report: str):
    key = _dart_key()
    if not key:
        _no_key_message()
        sys.exit(1)

    mapping = _load_corp_codes()
    if mapping is None:
        print("⚠️ 기업코드 매핑이 없습니다. 먼저 'python3 tools/kr_data.py setup'을 실행하세요.")
        sys.exit(1)

    code = _clean_code(code)
    info = mapping.get(code)
    if not info:
        print(f"❌ 종목코드 {code}에 대한 DART 기업코드를 찾지 못했습니다 (비상장이거나 매핑 갱신 필요)")
        return

    reprt_code = _REPORT_CODES.get(report, _REPORT_CODES["annual"])
    params = {
        "crtfc_key": key,
        "corp_code": info["corp_code"],
        "bsns_year": year,
        "reprt_code": reprt_code,
        "fs_div": "CFS",  # 연결재무제표 우선 조회
    }
    data = _curl_json("https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json", params)

    if data.get("status") != "000":
        # 연결재무제표가 없는 기업(자회사 없음 등)은 별도재무제표로 재시도
        params["fs_div"] = "OFS"
        data = _curl_json("https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json", params)

    if data.get("status") != "000":
        print(f"⚠️ DART 조회 실패 (코드 {data.get('status')}): {data.get('message')}")
        print("   연도(--year)나 보고서 종류(--report)를 바꿔서 재시도하거나 WebSearch로 보완하세요.")
        return

    rows = data.get("list", []) or []
    fs_label = "연결재무제표" if params["fs_div"] == "CFS" else "별도재무제표"
    print("=" * 60)
    print(f"재무제표: {info['corp_name']} ({code}) — {year}년 {report} [{fs_label}]")
    print("=" * 60)

    seen = set()
    for r in rows:
        name = (r.get("account_nm") or "").strip()
        label = _ACCOUNT_LABELS.get(name)
        if label and label not in seen:
            seen.add(label)
            amt = r.get("thstrm_amount", "-")
            prev = r.get("frmtrm_amount", "-")
            print(f"  {label:10s} 당기: {amt:>18s}원   전기: {prev:>18s}원")

    if not seen:
        print("  ⚠️ 핵심 계정을 자동으로 못 찾았습니다 — 원본 계정명 일부:")
        for r in rows[:20]:
            print(f"    {r.get('account_nm')}: {r.get('thstrm_amount')}")


# ---------------------------------------------------------------------------
# CLI 진입점
# ---------------------------------------------------------------------------

def main():
    # Windows 콘솔 기본 코드페이지(cp949 등)에서 한글/이모지가 깨지거나
    # UnicodeEncodeError가 나는 것을 방지 — 항상 UTF-8로 강제 출력.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="한국 주식 데이터 도구 — 네이버금융 시세/밸류에이션 + DART 재무제표",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    p_quote = sub.add_parser("quote", help="실시간 시세")
    p_quote.add_argument("code", help="종목코드 (예: 005930)")

    p_val = sub.add_parser("valuation", help="밸류에이션 지표 (PER/PBR/EPS/BPS 등)")
    p_val.add_argument("code", help="종목코드")

    p_search = sub.add_parser("search", help="종목코드 검색")
    p_search.add_argument("keyword", help="회사명 또는 키워드")

    sub.add_parser("setup", help="DART 기업코드 매핑 캐시 생성 (최초 1회, API 키 필요)")

    p_fin = sub.add_parser("financials", help="재무제표 (DART Open API, API 키 필요)")
    p_fin.add_argument("code", help="종목코드")
    p_fin.add_argument("--year", default="2025", help="사업연도 (기본값: 2025)")
    p_fin.add_argument("--report", choices=["annual", "q1", "half", "q3"], default="annual",
                        help="보고서 종류 (기본값: annual)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "quote":
        cmd_quote(args.code)
    elif args.command == "valuation":
        cmd_valuation(args.code)
    elif args.command == "search":
        cmd_search(args.keyword)
    elif args.command == "setup":
        cmd_setup()
    elif args.command == "financials":
        cmd_financials(args.code, args.year, args.report)


if __name__ == "__main__":
    main()
