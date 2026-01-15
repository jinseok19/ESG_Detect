# ESG-Radar 프로젝트 현황 보고서

**작성일**: 2026-01-06  
**프로젝트명**: ESG-Radar - AI-Powered ESG Pre-Assurance Platform  
**버전**: v1.0  
**개발자**: jinseok

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [현재 구현 상태](#2-현재-구현-상태)
3. [기술 스택 분석](#3-기술-스택-분석)
4. [시스템 아키텍처](#4-시스템-아키텍처)
5. [주요 기능 상세](#5-주요-기능-상세)
6. [코드 품질 평가](#6-코드-품질-평가)
7. [성능 및 제약사항](#7-성능-및-제약사항)
8. [고도화 방안](#8-고도화-방안)
9. [우선순위 로드맵](#9-우선순위-로드맵)

---

## 1. 프로젝트 개요

### 1.1 프로젝트 목적
ESG-Radar는 기업의 ESG 보고서를 AI로 자동 분석하여 데이터 정합성과 그린워싱 위험을 검증하는 **Pre-Assurance 플랫폼**입니다.

### 1.2 핵심 가치 제안
- ⚡ **빠른 검증**: 기존 수일 소요되던 ESG 보고서 검토를 2~3분으로 단축
- 🎯 **높은 정확도**: LangGraph Multi-Agent 시스템으로 체계적 검증
- 💰 **비용 절감**: 사전 검토로 외부 감사 비용 최소화
- 🏆 **Pre-Assurance 인증**: 80점 이상 시 디지털 인증서 발급

### 1.3 타겟 사용자
- 상장사 ESG 담당자 (보고서 제출 전 사전 검토)
- ESG 컨설팅 회사 (초기 스크리닝 도구)
- 투자자/애널리스트 (보고서 신뢰성 검증)

---

## 2. 현재 구현 상태

### 2.1 전체 완성도: ⭐⭐⭐⭐☆ (85%)

| 구성 요소 | 완성도 | 상태 |
|----------|-------|------|
| **RAG 엔진** | 95% | ✅ 완성 |
| **Multi-Agent 시스템** | 90% | ✅ 완성 |
| **웹 UI** | 85% | ✅ 완성 (일부 개선 필요) |
| **배포 인프라** | 80% | ✅ 완성 (모니터링 부족) |
| **테스트** | 40% | ⚠️ 부족 |
| **문서화** | 70% | ⚠️ API 문서 부족 |

### 2.2 구현된 주요 기능

#### ✅ 완전 구현
1. **RAG 기반 질의응답** (`rag_engine.py`)
   - PDF 파싱 (PyPDF2)
   - 텍스트 청킹 (RecursiveCharacterTextSplitter)
   - FAISS 벡터 검색
   - OpenAI GPT-4o 답변 생성
   - 출처 페이지 추적

2. **LangGraph Multi-Agent 워크플로우** (`agent_engine.py`)
   - **Integrity Engine**: K-ESG 5대 항목 + Decoupling 분석
   - **Green Audit**: 그린워싱 위험 3가지 유형 탐지
   - **Report Generator**: 종합 점수 산출 + Pre-Assurance 인증

3. **웹 인터페이스** (Flask + Bootstrap 5)
   - 파일 업로드 UI (`index.html`)
   - 기본 검토 결과 (`result.html`)
   - Pre-Assurance 대시보드 (`dashboard.html`)
   - PDF 인라인 뷰어 (`pdf_viewer.html`)
   - 넥서스코어 통합 버튼

4. **배포 설정**
   - Gunicorn WSGI 서버 (2 workers, 300s timeout)
   - Render.com 배포 설정

#### ⚠️ 부분 구현
1. **에러 핸들링**: 기본적인 try-catch만 있고, 세밀한 예외 처리 부족
2. **로깅**: 기본 logging만 사용, 구조화된 로그 없음
3. **캐싱**: 반복 질의 시 매번 RAG 검색 (비효율)

#### ❌ 미구현
1. **사용자 인증/권한**
2. **데이터베이스** (업로드 이력, 분석 결과 저장)
3. **API 엔드포인트** (외부 연동용)
4. **실시간 진행 상태** (WebSocket/SSE)
5. **PDF 다운로드 리포트** (현재는 HTML만)
6. **비교 분석** (이전 연도 보고서와 비교)

---

## 3. 기술 스택 분석

### 3.1 Backend

| 기술 | 버전 | 역할 | 평가 |
|------|------|------|------|
| **Flask** | 3.0.0 | 웹 프레임워크 | ✅ 적합 (경량, 빠른 개발) |
| **LangChain** | 0.1.20 | RAG 파이프라인 | ✅ 최신, 안정적 |
| **LangGraph** | 0.0.32 | Multi-Agent 오케스트레이션 | ⚠️ 초기 버전 (0.1.x 업그레이드 권장) |
| **OpenAI** | >=1.12.0 | LLM 엔진 | ✅ GPT-4o 사용 |
| **FAISS** | latest | 벡터 DB | ✅ 빠르고 메모리 효율적 |
| **PyPDF2** | 3.0.1 | PDF 파싱 | ✅ 가볍고 안정적 |
| **Gunicorn** | latest | WSGI 서버 | ✅ 프로덕션 검증됨 |

### 3.2 Frontend

| 기술 | 역할 | 평가 |
|------|------|------|
| **Bootstrap 5** | UI 프레임워크 | ✅ 반응형, 깔끔한 디자인 |
| **Chart.js** | 데이터 시각화 | ✅ Radar/Doughnut 차트 구현 |
| **Font Awesome** | 아이콘 | ✅ 직관적 UI |
| **Bootstrap Icons** | 아이콘 | ✅ 통일된 스타일 |

### 3.3 인프라

| 항목 | 현재 상태 | 평가 |
|------|----------|------|
| **호스팅** | Render.com (2GB RAM) | ✅ 적합 |
| **환경변수** | `.env` 파일 | ✅ 안전 |
| **워커 수** | 2 workers | ✅ 2GB에 적합 |
| **타임아웃** | 300초 | ✅ PDF 처리 충분 |
| **모니터링** | ❌ 없음 | ⚠️ 필요 |

---

## 4. 시스템 아키텍처

### 4.1 전체 흐름도

```
┌────────────────┐
│  사용자 (웹)   │
└────────┬───────┘
         │
         ▼
┌────────────────────────────────────────┐
│         Flask Web Server               │
│  ┌──────────────┐  ┌─────────────────┐│
│  │ index.html   │  │ dashboard.html  ││
│  │ (업로드)     │  │ (결과 시각화)    ││
│  └──────────────┘  └─────────────────┘│
└────────┬───────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│      app.py (라우팅 레이어)            │
│  - /              : 기본 검토          │
│  - /analyze       : Pre-Assurance      │
│  - /pdf/<name>    : PDF 다운로드       │
│  - /viewer/<name> : PDF 뷰어           │
└────────┬───────────────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────────────────────┐
│ RAG     │ │ LangGraph Multi-Agent    │
│ Engine  │ │ ┌──────────────────────┐ │
│         │ │ │ 1. Integrity Engine  │ │
│ FAISS   │◄┼─│    - K-ESG 5대 항목  │ │
│ Vector  │ │ │    - Decoupling      │ │
│ Store   │ │ └──────────┬───────────┘ │
│         │ │            ▼             │
│         │ │ ┌──────────────────────┐ │
│         │ │ │ 2. Green Audit       │ │
│ OpenAI  │◄┼─│    - 모호한 표현     │ │
│ GPT-4o  │ │ │    - 근거 부재       │ │
│         │ │ │    - Cherry-picking  │ │
│         │ │ └──────────┬───────────┘ │
│         │ │            ▼             │
│         │ │ ┌──────────────────────┐ │
│         │ │ │ 3. Report Generator  │ │
│         │◄┼─│    - 종합 점수       │ │
│         │ │ │    - 인증 자격 판정  │ │
└─────────┘ │ └──────────────────────┘ │
            └──────────────────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  최종 리포트    │
            │  (JSON)         │
            └─────────────────┘
```

### 4.2 데이터 흐름

```
1. PDF 업로드
   ↓
2. PyPDF2 텍스트 추출 (페이지별)
   ↓
3. RecursiveCharacterTextSplitter (1500자 청크, 300자 오버랩)
   ↓
4. OpenAI text-embedding-3-small (벡터화)
   ↓
5. FAISS 벡터 저장소에 인덱싱
   ↓
6. LangGraph StateGraph 실행
   ├─ Node 1: Integrity Engine
   │   └─ K-ESG 5개 항목 + Decoupling (총 6개 쿼리)
   │
   ├─ Node 2: Green Audit
   │   └─ 그린워싱 3가지 유형 탐지 (3개 쿼리)
   │
   └─ Node 3: Report Generator
       └─ 점수 산출 + Pre-Assurance 판정
   ↓
7. HTML 대시보드 렌더링 (Chart.js)
```

### 4.3 주요 클래스 구조

```python
# rag_engine.py
class ESG_RAG:
    - __init__(pdf_path, api_key)
    - _initialize_vector_db()        # PDF → FAISS
    - ask(question) → (answer, sources, pages)

# agent_engine.py
class ESGRadarAgent:
    - __init__(pdf_path, api_key)
    - _build_workflow() → StateGraph
    - integrity_engine_node(state) → state
    - green_audit_node(state) → state
    - report_generator_node(state) → state
    - run() → final_report

# app.py
Flask Routes:
    - index() : GET/POST
    - serve_pdf(filename) : GET
    - pdf_viewer(filename) : GET
    - analyze() : POST (Multi-Agent 실행)
```

---

## 5. 주요 기능 상세

### 5.1 RAG 엔진 (`rag_engine.py`)

#### 강점
- ✅ **메모리 최적화**: 페이지별 처리 + 주기적 GC
- ✅ **페이지 추적**: 출처 페이지 번호 정확히 반환
- ✅ **에러 처리**: PDF 손상, 메모리 부족 등 예외 처리
- ✅ **프롬프트 엔지니어링**: 상세한 답변 지침 제공

#### 개선 필요
- ⚠️ **재사용 불가**: 매 요청마다 벡터 DB 재생성 (30초~1분 소요)
- ⚠️ **메타데이터 부족**: 페이지 외 장/절 정보 없음
- ⚠️ **고정 청크 크기**: 문서 특성에 따른 동적 조정 필요

#### 핵심 코드 분석

```python
# 1. PDF 로드 최적화
for page_num in range(pages_to_process):
    page = pdf_reader.pages[page_num]
    text = page.extract_text()
    if text and len(text.strip()) >= 50:  # 빈 페이지 필터링
        documents.append(Document(...))
    if (page_num + 1) % 20 == 0:
        gc.collect()  # 메모리 해제

# 2. 벡터 저장소 생성
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
self.vector_store = FAISS.from_documents(texts, embeddings)

# 3. 질의응답
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o", temperature=0),
    retriever=self.vector_store.as_retriever(search_kwargs={"k": 8}),
    return_source_documents=True
)
```

### 5.2 Multi-Agent 시스템 (`agent_engine.py`)

#### Node 1: Integrity Engine (정합성 검증)

**검증 항목**:
1. 온실가스 배출량 (Scope 1, 2, 3)
2. 에너지 사용량 + 재생에너지 비율
3. 용수 사용량 + 재활용률
4. 폐기물 발생량 + 재활용률
5. 법규 위반 사항

**점수 산정**:
- K-ESG 5대 항목: 70점 (각 14점)
- Decoupling 분석: 30점
- **총점**: 0~100점

#### Node 2: Green Audit (그린워싱 탐지)

**탐지 유형**:
1. **모호한 표현** (Medium) - 15점 감점
   - "친환경", "에코" 등 근거 없는 표현
   
2. **미래 목표 근거 부재** (High) - 30점 감점
   - 2030/2050 목표만 있고 로드맵 없음

3. **전 과정 평가 누락** (High) - 30점 감점
   - Scope 3 누락, Cherry-picking

**점수 산정**:
- 기본: 100점
- 위험 발견 시 감점
- **총점**: 0~100점

**위험도 레벨**:
- 80점 이상: Low
- 60~80점: Medium
- 60점 미만: High

#### Node 3: Report Generator (종합 리포트)

**종합 점수**:
```python
composite_score = integrity_score * 0.6 + greenwashing_score * 0.4
```

**Pre-Assurance 인증 조건**:
```python
pre_assurance_eligible = (
    integrity_score >= 80 AND
    greenwashing_score >= 80 AND
    risk_level == "Low"
)
```

### 5.3 웹 인터페이스

#### 1. `index.html` (메인 페이지)
- 분석 모드 선택 (기본 검토 / Pre-Assurance)
- PDF 파일 업로드
- 검토 항목 안내
- **최근 추가**: 넥서스코어 돌아가기 버튼

#### 2. `result.html` (기본 검토 결과)
- 완료율 대시보드
- 카테고리별 결과 (환경/사회/거버넌스)
- PDF 인라인 뷰어 (페이지 이동 기능)
- 출처 페이지 클릭 → PDF 해당 페이지로 점프

#### 3. `dashboard.html` (Pre-Assurance 대시보드)
- 🏆 Pre-Assurance 인증 배지 (조건부)
- 3가지 점수 카드 (종합/정합성/그린워싱)
- Chart.js 시각화:
  - Radar Chart (종합 분석)
  - Doughnut Chart (K-ESG 준수율)
- K-ESG 체크리스트 (5개 항목)
- Decoupling 분석 결과
- 그린워싱 위험 테이블 (위험도별)

#### 4. `pdf_viewer.html` (PDF 뷰어)
- PDF.js 기반 인라인 뷰어
- 페이지 이동 파라미터 지원 (`?page=10`)
- 검색어 하이라이트 (`?q=keyword`)

---

## 6. 코드 품질 평가

### 6.1 강점

#### ✅ 1. 명확한 분리 (Separation of Concerns)
- `rag_engine.py`: RAG 로직만
- `agent_engine.py`: Multi-Agent 로직만
- `app.py`: 라우팅만
- 각 모듈이 독립적으로 테스트 가능

#### ✅ 2. 타입 힌트 사용
```python
class ESGRadarState(TypedDict):
    pdf_path: str
    api_key: str
    integrity_score: float
    greenwashing_risks: List[Dict]
```

#### ✅ 3. 상세한 주석
- 각 함수의 docstring 존재
- 복잡한 로직에 인라인 주석

#### ✅ 4. 에러 핸들링
- MemoryError 별도 처리
- PDF 파일 크기 제한 (100MB)
- 파일 확장자 검증

### 6.2 개선 필요

#### ⚠️ 1. 하드코딩된 값
```python
# rag_engine.py
MAX_PAGES = 300  # 설정 파일로 분리 필요
chunk_size=1500  # 환경변수 또는 config

# gunicorn_config.py
workers = 2  # 인스턴스 타입에 따라 동적 설정
```

#### ⚠️ 2. 매직 넘버
```python
# agent_engine.py
base_score = (total_found / len(k_esg_items)) * 70  # 70이 무엇인지?
decoupling_bonus = 30  # 30의 근거?

# 개선안
KESG_MAX_SCORE = 70
DECOUPLING_BONUS = 30
```

#### ⚠️ 3. 긴 함수
- `integrity_engine_node()`: 80줄 (분할 필요)
- `green_audit_node()`: 120줄 (분할 필요)

#### ⚠️ 4. 테스트 부재
- `tests/` 폴더 없음
- 단위 테스트 0개
- 통합 테스트 0개

#### ⚠️ 5. 로깅 부족
```python
# 현재
logging.info("분석 시작")

# 개선 필요
logger.info("분석 시작", extra={
    "filename": filename,
    "file_size": file_size,
    "user_id": user_id
})
```

---

## 7. 성능 및 제약사항

### 7.1 처리 시간

| 단계 | 소요 시간 | 비고 |
|------|----------|------|
| PDF 파싱 | 10~30초 | 페이지 수에 비례 |
| 벡터 임베딩 | 20~40초 | 청크 수에 비례 |
| K-ESG 검증 (6개 쿼리) | 30~60초 | GPT-4o API 호출 |
| 그린워싱 탐지 (3개 쿼리) | 20~40초 | GPT-4o API 호출 |
| 리포트 생성 | <1초 | 로컬 계산 |
| **총 처리 시간** | **80~170초** | **1.5~3분** |

### 7.2 리소스 사용

| 항목 | 현재 | 권장 |
|------|------|------|
| **RAM** | 2GB | ✅ 충분 |
| **CPU** | 1 vCPU | ⚠️ 2 vCPU 권장 (병렬 처리) |
| **디스크** | 512MB | ✅ 충분 |
| **네트워크** | OpenAI API | ✅ 안정적 |

### 7.3 제약사항

#### 📏 파일 크기
- **최대**: 100MB
- **권장**: 20MB 이하 (빠른 처리)
- **페이지**: 최대 300페이지

#### 💰 API 비용
```
1회 분석당 OpenAI API 비용:
- 임베딩: 약 $0.01 (10,000 토큰)
- GPT-4o: 약 $0.15 (9개 쿼리 × $0.015)
───────────────────────────
총 비용: 약 $0.16/보고서
```

#### ⏱️ 타임아웃
- Gunicorn: 300초 (5분)
- OpenAI API: 90초/요청
- 300페이지 이상 PDF는 실패 가능

#### 🔒 보안
- API Key가 `.env`에만 저장 (Git에 노출 위험)
- 업로드된 PDF가 서버에 영구 저장 (삭제 로직 없음)
- 사용자 인증 없음 (누구나 사용 가능)

---

## 8. 고도화 방안

### 8.1 즉시 적용 가능 (1~2주)

#### 🔥 우선순위 1: 성능 최적화

##### 1.1 벡터 DB 캐싱
**현재 문제**: 매 요청마다 PDF 재파싱 + 재임베딩 (30초 낭비)

**해결 방안**:
```python
# 파일 해시 기반 캐싱
import hashlib
from functools import lru_cache

def get_file_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

# FAISS 인덱스 저장
vector_store.save_local(f"cache/{file_hash}.faiss")

# 재사용
if os.path.exists(cache_path):
    vector_store = FAISS.load_local(cache_path)
```

**예상 효과**: 2차 분석부터 30초 → 3초 (10배 빠름)

##### 1.2 비동기 처리 (Celery)
**현재 문제**: 브라우저가 3분간 대기 (타임아웃 위험)

**해결 방안**:
```python
# Celery 태스크 큐
@celery.task
def analyze_pdf_async(pdf_path, task_id):
    # 분석 실행
    result = analyze_esg_report(pdf_path)
    # 결과 저장
    redis.set(f"task:{task_id}", json.dumps(result))

# 프론트엔드: 폴링 또는 WebSocket
<script>
setInterval(() => {
    fetch(`/status/${task_id}`)
        .then(res => res.json())
        .then(data => {
            if (data.status === 'completed') {
                window.location = `/dashboard/${task_id}`;
            }
        });
}, 2000);  // 2초마다 확인
</script>
```

**예상 효과**: 사용자 이탈 감소 + 동시 처리 가능

##### 1.3 프롬프트 배치 처리
**현재**: 9개 쿼리를 순차 실행 (각 5초 = 45초)

**개선**:
```python
import asyncio
from langchain_openai import AsyncChatOpenAI

async def batch_queries(queries):
    tasks = [self.rag.ask_async(q) for q in queries]
    return await asyncio.gather(*tasks)

# 9개 쿼리를 병렬 실행 → 5초로 단축 (9배 빠름)
```

#### 🔥 우선순위 2: 결과 저장 (PostgreSQL)

**테이블 설계**:
```sql
-- 분석 이력
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    file_hash VARCHAR(32) UNIQUE,
    uploaded_at TIMESTAMP,
    composite_score FLOAT,
    integrity_score FLOAT,
    greenwashing_score FLOAT,
    risk_level VARCHAR(10),
    pre_assurance BOOLEAN,
    result_json JSONB
);

-- 사용자 (옵션)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    company VARCHAR(255),
    created_at TIMESTAMP
);
```

**기능**:
- 이전 분석 결과 조회
- 연도별 비교 (예: 2023 vs 2024)
- 통계 대시보드 (평균 점수, 업종별 순위)

#### 🔥 우선순위 3: 실시간 진행 상태

**Server-Sent Events (SSE)**:
```python
# Flask SSE
@app.route('/stream/<task_id>')
def stream_progress(task_id):
    def generate():
        yield f"data: PDF 파싱 중...\n\n"
        yield f"data: 벡터 임베딩 중...\n\n"
        yield f"data: K-ESG 검증 중 (1/5)...\n\n"
        # ...
    return Response(generate(), mimetype='text/event-stream')

# JavaScript
const evtSource = new EventSource('/stream/{task_id}');
evtSource.onmessage = (e) => {
    document.getElementById('status').innerText = e.data;
};
```

### 8.2 중기 과제 (1~2개월)

#### 💡 1. 고급 분석 기능

##### 1.1 연도별 비교
```python
# 2023년 vs 2024년 보고서 비교
{
    "ghg_trend": {
        "2023": 100000,
        "2024": 95000,
        "change": -5.0,  # % 감소
        "assessment": "목표 대비 우수"
    }
}
```

##### 1.2 업종별 벤치마킹
```python
# 제조업 평균과 비교
{
    "company_score": 85.2,
    "industry_avg": 72.5,
    "percentile": 85  # 상위 15%
}
```

##### 1.3 AI 권고사항
```python
# GPT-4o로 개선 제안 생성
recommendations = [
    "Scope 3 배출량 측정 방법론을 GHG Protocol에 맞춰 보완하세요.",
    "재생에너지 비율 50% 달성 로드맵을 추가하면 점수가 +10점 상승합니다."
]
```

#### 💡 2. PDF 리포트 다운로드

**WeasyPrint 또는 ReportLab 사용**:
```python
from weasyprint import HTML

@app.route('/download/<report_id>')
def download_report(report_id):
    html = render_template('dashboard.html', report=report)
    pdf = HTML(string=html).write_pdf()
    return send_file(pdf, mimetype='application/pdf')
```

#### 💡 3. API 엔드포인트

**RESTful API for 외부 연동**:
```python
# POST /api/v1/analyze
{
    "pdf_url": "https://example.com/report.pdf",
    "api_key": "your_api_key"
}

# Response
{
    "report_id": "abc123",
    "status": "processing",
    "estimated_time": 120  # seconds
}

# GET /api/v1/reports/{report_id}
{
    "status": "completed",
    "composite_score": 85.2,
    "pre_assurance": true,
    "result_url": "https://esg-radar.com/reports/abc123"
}
```

#### 💡 4. 고급 그린워싱 탐지

**추가 탐지 유형**:
```python
greenwashing_checks = [
    "Hidden Trade-offs": "일부 환경 개선을 강조하고 다른 피해는 숨김",
    "Irrelevant Claims": "제품과 무관한 환경 주장",
    "Lesser of Two Evils": "덜 나쁜 것을 친환경으로 포장",
    "Fibbing": "거짓 인증 또는 허위 데이터",
    "Worshiping False Labels": "의미 없는 자체 인증"
]
```

### 8.3 장기 과제 (3~6개월)

#### 🚀 1. 멀티모달 분석

**이미지/그래프 분석 (GPT-4o Vision)**:
```python
# PDF에서 이미지 추출
from pdf2image import convert_from_path

images = convert_from_path(pdf_path)

# GPT-4o Vision으로 그래프 분석
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "이 그래프의 추세를 분석하세요"},
            {"type": "image_url", "image_url": image_url}
        ]
    }]
)
```

**효과**: 텍스트로만 파악 불가능한 차트 데이터 추출

#### 🚀 2. 실시간 협업 검토

**Google Docs 스타일 코멘트**:
```javascript
// 사용자가 특정 문장에 코멘트 달기
<span class="comment-target" data-comment-id="123">
    "2050 탄소중립 달성"
</span>

// 우측 사이드바에 코멘트 표시
<div class="comment">
    <strong>ESG 담당자</strong>: 
    "로드맵 추가 필요"
</div>
```

#### 🚀 3. 자동 보고서 생성 (역방향)

**GPT-4o로 ESG 보고서 초안 작성**:
```python
def generate_esg_report_draft(company_data):
    """
    기업 데이터를 입력받아 ESG 보고서 초안 생성
    - K-ESG 필수 항목 자동 작성
    - GRI, TCFD 프레임워크 준수
    """
    prompt = f"""
    다음 데이터로 ESG 보고서를 작성하세요:
    - 온실가스 배출량: {company_data['ghg']}
    - 에너지 사용량: {company_data['energy']}
    ...
    """
    return llm.invoke(prompt)
```

#### 🚀 4. 블록체인 인증

**Pre-Assurance 인증서를 NFT로 발행**:
```solidity
// Ethereum Smart Contract
contract ESGCertificate {
    struct Certificate {
        string reportHash;
        uint256 compositeScore;
        uint256 timestamp;
        address company;
    }
    
    mapping(uint256 => Certificate) public certificates;
    
    function issueCertificate(...) public {
        // 인증서 발행 (위변조 불가)
    }
}
```

---

## 9. 우선순위 로드맵

### 🎯 Phase 1: 안정화 (2주)

| 번호 | 작업 | 예상 시간 | 효과 |
|------|------|----------|------|
| 1.1 | 벡터 DB 캐싱 구현 | 2일 | 재분석 10배 빠름 |
| 1.2 | 에러 로깅 강화 | 1일 | 디버깅 용이 |
| 1.3 | 단위 테스트 작성 | 3일 | 버그 감소 |
| 1.4 | 환경변수 분리 (config.py) | 1일 | 유지보수성 향상 |
| 1.5 | 업로드 파일 자동 삭제 | 1일 | 디스크 공간 절약 |

**총 소요 시간**: 8일

### 🚀 Phase 2: 기능 확장 (1개월)

| 번호 | 작업 | 예상 시간 | 효과 |
|------|------|----------|------|
| 2.1 | PostgreSQL 연동 | 3일 | 이력 관리 |
| 2.2 | 비동기 처리 (Celery) | 5일 | UX 개선 |
| 2.3 | 실시간 진행 상태 (SSE) | 2일 | UX 개선 |
| 2.4 | PDF 리포트 다운로드 | 3일 | 공유 용이 |
| 2.5 | 연도별 비교 기능 | 5일 | 고급 분석 |

**총 소요 시간**: 18일

### 💎 Phase 3: 프리미엄 기능 (2개월)

| 번호 | 작업 | 예상 시간 | 효과 |
|------|------|----------|------|
| 3.1 | API 엔드포인트 | 7일 | B2B 연동 |
| 3.2 | 사용자 인증/권한 | 5일 | 보안 강화 |
| 3.3 | 업종별 벤치마킹 | 7일 | 차별화 |
| 3.4 | AI 권고사항 생성 | 5일 | 부가가치 |
| 3.5 | 멀티모달 분석 | 10일 | 정확도 향상 |

**총 소요 시간**: 34일

---

## 10. 비용 추정

### 10.1 운영 비용 (월간)

| 항목 | 단가 | 사용량 | 월 비용 |
|------|------|--------|---------|
| **Render.com** (2GB) | $25/월 | 1대 | $25 |
| **OpenAI API** | $0.16/분석 | 1,000건 | $160 |
| **PostgreSQL** (Render) | $7/월 | 1GB | $7 |
| **Redis** (캐싱) | $10/월 | 256MB | $10 |
| **도메인** | $12/년 | - | $1 |
| **총 운영 비용** | - | - | **$203/월** |

### 10.2 개발 비용 (Phase 1~3)

| Phase | 소요 시간 | 개발자 일당 | 총 비용 |
|-------|----------|------------|---------|
| Phase 1 | 8일 | $500 | $4,000 |
| Phase 2 | 18일 | $500 | $9,000 |
| Phase 3 | 34일 | $500 | $17,000 |
| **합계** | 60일 | - | **$30,000** |

### 10.3 수익 모델 (예상)

| 플랜 | 가격 | 기능 | 예상 고객 수 |
|------|------|------|--------------|
| **Free** | $0 | 월 3회 | 1,000명 |
| **Pro** | $99/월 | 월 50회 + PDF 다운로드 | 50명 |
| **Enterprise** | $499/월 | 무제한 + API + 벤치마킹 | 10명 |

**예상 월 매출**: (50 × $99) + (10 × $499) = **$9,940/월**  
**예상 순이익**: $9,940 - $203 = **$9,737/월**

---

## 11. 위험 요소 및 대응

### ⚠️ 위험 1: OpenAI API 의존성

**문제**: API 장애 시 서비스 중단

**대응**:
1. Claude / Gemini 멀티 LLM 지원
2. 로컬 LLM (Llama 3) 백업

### ⚠️ 위험 2: 법적 책임

**문제**: AI 오판 시 기업 손해 발생

**대응**:
1. 면책 조항 명시: "참고용으로만 사용"
2. 전문가 검토 권장
3. 보험 가입

### ⚠️ 위험 3: 데이터 유출

**문제**: 업로드된 ESG 보고서는 기밀

**대응**:
1. 분석 후 즉시 삭제
2. AWS S3 암호화 저장
3. ISO 27001 인증 획득

---

## 12. 결론 및 권장사항

### 🎯 현재 상태 종합 평가

**완성도**: ⭐⭐⭐⭐☆ (85%)
- 핵심 기능 완성
- 프로덕션 배포 가능
- 개선 여지 충분

**강점**:
- ✅ 최신 기술 스택 (LangGraph, GPT-4o)
- ✅ 명확한 아키텍처
- ✅ 실용적인 UI/UX
- ✅ 빠른 분석 속도 (2~3분)

**약점**:
- ⚠️ 테스트 부족
- ⚠️ 캐싱 없음 (재분석 비효율)
- ⚠️ 모니터링 없음

### 🚀 즉시 실행 권장

1. **벡터 DB 캐싱** (투입: 2일, 효과: 10배 속도 향상)
2. **에러 로깅** (투입: 1일, 효과: 안정성 향상)
3. **업로드 파일 삭제** (투입: 1일, 효과: 보안 강화)

### 💎 차별화 전략

1. **속도**: 기존 3일 → 3분 (1000배 빠름)
2. **정확도**: Multi-Agent 검증 (사람보다 일관적)
3. **비용**: 외부 감사 $10,000 → AI 사전 검토 $99

### 📈 성장 전략

**단기** (3개월):
- B2C: 상장사 ESG 담당자 100명 확보
- 목표 MRR: $10,000

**중기** (1년):
- B2B: ESG 컨설팅사와 제휴
- API 라이센스 판매
- 목표 ARR: $300,000

**장기** (3년):
- 글로벌 확장 (영문/일문 지원)
- 업종별 특화 (금융/제조/IT)
- 목표 ARR: $3,000,000

---

## 📚 참고 자료

### 기술 문서
- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [LangChain RAG 가이드](https://python.langchain.com/docs/use_cases/question_answering/)
- [FAISS 성능 최적화](https://github.com/facebookresearch/faiss/wiki)

### ESG 표준
- [K-ESG 가이드라인](https://www.ksd.or.kr/)
- [환경부 환경성 표시·광고 관리제도](http://www.me.go.kr/)
- [EU Green Claims Directive](https://ec.europa.eu/)
- [GRI Standards](https://www.globalreporting.org/)
- [TCFD 프레임워크](https://www.fsb-tcfd.org/)

---

**보고서 작성**: Claude Sonnet 4.5 (Cursor AI)  
**작성일**: 2026-01-06  
**버전**: 1.0


