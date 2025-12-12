# ESG-Radar 🚀

AI-Powered ESG Pre-Assurance Platform - LangGraph 기반 Multi-Agent 검증 시스템

## 🌟 주요 기능

### 1. **Integrity Engine** (데이터 정합성 검증)
- **K-ESG 5대 필수 항목 자동 검증**
  - ✅ 온실가스 배출량 (Scope 1, 2, 3)
  - ✅ 에너지 사용량
  - ✅ 용수 사용량
  - ✅ 폐기물 발생량
  - ✅ 법규 위반 사항

- **Decoupling 분석**
  - 매출/생산량 증가 대비 배출량 감소 추이 확인
  - 탈동조화(Decoupling) 설명 여부 검증

### 2. **Green Audit** (그린워싱 위험 탐지)
- **환경부 고시 + EU Green Claims Directive 기준**
  - 모호한 표현 (Vague Claims) 탐지
  - 미래 목표의 근거 부재 확인
  - 전 과정 평가 누락 (Cherry-picking) 검사

- **위험도 레벨 자동 산정**
  - High / Medium / Low

### 3. **Report Generator** (종합 리포트)
- **0-100점 척도 점수화**
  - Integrity Score (데이터 정합성)
  - Greenwashing Score (그린워싱 위험도)
  - Composite Score (종합 점수)

- **Pre-Assurance 인증**
  - 두 점수 모두 80점 이상 시 자격 획득
  - 디지털 인증서 배지 발급

## 🏗️ 기술 스택

### Backend
- **Flask** - 웹 프레임워크
- **LangGraph** - Multi-Agent 워크플로우 오케스트레이션
- **LangChain** - RAG (Retrieval-Augmented Generation)
- **OpenAI GPT-4o** - LLM 엔진
- **FAISS** - 벡터 DB (임베딩 검색)
- **PyPDF2** - PDF 파싱 (메모리 최적화)

### Frontend
- **Bootstrap 5** - UI 프레임워크
- **Chart.js** - 데이터 시각화 (Radar Chart, Doughnut Chart)
- **Font Awesome** - 아이콘

### Deployment
- **Render.com** - 클라우드 호스팅 (2GB RAM 인스턴스)
- **Gunicorn** - WSGI 서버 (타임아웃 300초)

## 📦 설치 및 실행

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/yourusername/ESG_Detect.git
cd ESG_Detect

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일 생성:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 로컬 실행

```bash
python app.py
```

브라우저에서 http://localhost:5000 접속

### 4. Render 배포

```bash
git add .
git commit -m "Deploy ESG-Radar"
git push
```

Render 대시보드 설정:
- **Start Command**: `gunicorn -c gunicorn_config.py app:app`
- **Instance Type**: Standard (2GB RAM) 이상 권장

## 🎯 사용 방법

### 1. 기본 검토 (30초~1분)
- 주요 ESG 항목 간단 확인
- Scope 1, 2, 3 배출량 데이터 검증

### 2. Pre-Assurance 분석 (2~3분) ⭐ 추천
1. **PDF 업로드**: ESG 보고서 파일 선택
2. **AI 분석 시작**: 
   - Integrity Engine (정합성 검증)
   - Green Audit (그린워싱 탐지)
   - Report Generator (최종 리포트)
3. **대시보드 확인**:
   - 종합 점수 및 위험도
   - K-ESG 체크리스트
   - 그린워싱 위험 사항
   - Pre-Assurance 인증서 (80점 이상)

## 📊 분석 결과 예시

```json
{
  "composite_score": 85.2,
  "integrity_score": 88.0,
  "greenwashing_score": 81.0,
  "risk_level": "Low",
  "pre_assurance_eligible": true,
  "k_esg_completion": 100.0,
  "total_risks_found": 1
}
```

## 🔧 아키텍처

```
┌─────────────┐
│   PDF File  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  PyPDF2     │ ─► 텍스트 추출 (페이지 단위)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FAISS      │ ─► 벡터 임베딩 저장
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│   LangGraph StateGraph      │
├─────────────────────────────┤
│  1. Integrity Engine Node   │ ─► K-ESG 검증 + Decoupling
│  2. Green Audit Node        │ ─► 그린워싱 탐지
│  3. Report Generator Node   │ ─► 최종 점수 산출
└──────┬──────────────────────┘
       │
       ▼
┌─────────────┐
│  Dashboard  │ ─► Chart.js 시각화 + 인증서
└─────────────┘
```

## 📝 라이선스

MIT License

## 👥 기여자

- **개발자**: jinseok
- **프로젝트**: ESG-Radar v1.0

## 🔗 관련 링크

- [환경부 환경성 표시·광고 관리제도](http://www.me.go.kr/)
- [EU Green Claims Directive](https://ec.europa.eu/)
- [K-ESG 가이드라인](https://www.ksd.or.kr/)

---

**ESG-Radar** - Powered by OpenAI GPT-4o & LangGraph 🚀
