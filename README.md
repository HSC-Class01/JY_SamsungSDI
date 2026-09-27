# 삼성SDI OpenDART 재무 분석 대시보드

<a href="https://hsc-class01.github.io/JY_SamsungSDI/"><img src="assets/samsung-sdi-logo.svg" alt="🔗 삼성SDI 대시보드 바로가기" width="230"></a>

### [🔗 대시보드 바로가기](https://hsc-class01.github.io/JY_SamsungSDI/)

삼성SDI(종목코드 `006400`, OpenDART corp_code `00126362`)의 사업보고서·반기보고서·분기보고서를 수집하고 핵심 재무수치와 재무비율을 자동 분석하는 프로젝트입니다.

> **데이터 범위 주의:** OpenDART의 단일회사 전체 재무제표 API는 공식적으로 2015년 이후 사업연도부터 제공됩니다. 따라서 2010~2014년은 DART 정기보고서 원문을 수집·보관하고, API 기반 구조화 재무수치 표는 2015년 이후를 기본 범위로 합니다. 2010년 이후의 구조화 수치를 추가하려면 과거 보고서 원문/XBRL 별도 추출 단계를 확장할 수 있습니다.

## Dashboard

상단에는 핵심 KPI와 시계열 figures, 중간에는 수익성·안정성·성장성 지표, 하단에는 **Annual / Half-year / Quarterly** 3개 표와 국내 peer firms를 배치합니다. 오른쪽 플로팅 메뉴에서 현재 화면을 PDF로 출력하거나 기간별 Excel을 내려받을 수 있습니다.

## 수집 대상

| 구분 | OpenDART `reprt_code` |
|---|---:|
| 사업보고서 / Annual | `11011` |
| 반기보고서 / Half-year | `11012` |
| 1분기보고서 / Quarterly | `11013` |
| 3분기보고서 / Quarterly | `11014` |

OpenDART 공식 문서에서 위 보고서 코드와 `fnlttSinglAcntAll.json` API를 사용합니다.

## 주요 재무수치

- 매출액
- 매출원가
- 매출총이익
- 영업이익
- 법인세차감전이익
- 당기순이익
- 자산총계 / 유동자산
- 현금및현금성자산
- 매출채권
- 재고자산
- 부채총계 / 유동부채
- 자본총계
- 영업현금흐름
- CAPEX
- 잉여현금흐름(FCF)

## 주요 재무비율

- 매출성장률
- 매출총이익률
- 영업이익률
- 순이익률
- ROA
- ROE
- 유동비율
- 당좌비율
- 부채비율
- 재고회전율
- DSO
- CFO 전환율
- FCF

모든 비율은 공개된 재무제표 계정에서 코드로 계산하며, 값이 없는 계정은 억지로 추정하지 않고 `—`로 표시합니다.

## 자동화

GitHub Actions가 **매월 1일 09:00 KST**에 실행되도록 설정합니다.

```text
GitHub Actions
      ↓
OpenDART disclosure list
      ↓
사업/반기/분기 보고서 확인
      ↓
DART 원문 ZIP 저장
      ↓
구조화 재무제표 API 수집
      ↓
계정명 정규화
      ↓
재무비율 계산
      ↓
dashboard.json / CSV 갱신
      ↓
GitHub Pages 배포
```

보고서가 이미 저장되어 있으면 중복 다운로드하지 않으며, 새 보고서만 추가합니다.

## 국내 Peer firms

삼성SDI의 핵심 사업인 2차전지와 전자재료를 고려해 국내 비교기업을 아래와 같이 정리합니다. 이는 **사업 비교를 위한 peer set**이며, 재무지표를 단순 평균하거나 투자 판단을 자동화하는 순위표가 아닙니다.

| 기업 | 주요 비교 영역 | 비고 |
|---|---|---|
| LG에너지솔루션 | EV/ESS 배터리 | 국내 배터리 셀 제조사 |
| SK이노베이션 / SK온 | EV/ESS 배터리 | 배터리 사업 비교 시 SK온 중심으로 해석 |
| LG화학 | 배터리 소재·화학 | 소재 및 배터리 밸류체인 비교 |
| 포스코퓨처엠 | 양극재·음극재 | 배터리 소재 비교 |
| 에코프로비엠 | 양극재 | 양극재 사업 비교 |
| 엘앤에프 | 양극재 | 양극재 사업 비교 |

Peer firm은 제품·사업영역이 완전히 동일하지 않으므로 dashboard에서는 사업영역을 함께 표시합니다.

## API Key 설정

1. OpenDART에서 인증키를 발급합니다.
2. GitHub repository → **Settings → Secrets and variables → Actions → New repository secret**
3. Secret 이름: `DART_API_KEY`
4. Secret 값: OpenDART에서 발급받은 40자리 인증키
5. **Settings → Pages**에서 Build and deployment의 Source를 `GitHub Actions`로 설정합니다.
6. **Actions → Update OpenDART data and deploy dashboard → Run workflow**를 한 번 실행합니다.

API 키는 코드, README, ZIP에 넣지 않습니다.

## 로컬 실행

```bash
python -m pip install -r requirements.txt
export DART_API_KEY="YOUR_KEY"
python scripts/fetch_opendart.py --start-year 2010
python scripts/analyze.py
python -m http.server 8000
```

Windows PowerShell:

```powershell
$env:DART_API_KEY="YOUR_KEY"
python scripts/fetch_opendart.py --start-year 2010
python scripts/analyze.py
python -m http.server 8000
```

브라우저에서 `http://localhost:8000`을 엽니다.

## ZIP

`python scripts/build_zip.py`를 실행하면 숨김 파일/폴더(`.git`, `.github`, `.env`, `__pycache__` 등)를 제외한 배포용 ZIP이 생성됩니다.

## Sources

- OpenDART: https://opendart.fss.or.kr/
- Repository: https://github.com/HSC-Class01/JY_SamsungSDI
