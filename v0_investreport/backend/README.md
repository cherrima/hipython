# FastAPI Backend - LLM 투자 보고서 생성 서비스

## 설치 및 실행

### 1. 가상환경 생성 (선택사항)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 서버 실행 (uvicorn)
```bash
# 개발 모드 (자동 리로드)
uvicorn main:app --reload --port 8000

# 프로덕션 모드
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. API 문서 확인
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/companies` | 모든 회사 목록 조회 |
| GET | `/api/companies/{ticker}` | 특정 회사 전체 데이터 조회 |
<!-- | GET | `/api/companies/{ticker}/basic-info` | 기본정보만 조회 (dict/json) |
| GET | `/api/companies/{ticker}/financial-data` | 재무 데이터 조회 (DataFrame 형식) | -->
| GET | `/api/reports/{ticker}` | 투자보고서 조회 (Markdown) |
<!-- | GET | `/api/reports/{ticker}/full` | 투자보고서(전체) 조회 (제목 제외 Markdown) | -->
| GET | `/api/search?q={query}` | 회사 검색 |
| GET | `/health` | 헬스 체크 |

## 데이터 형식

### 기본정보 (dict/json 형식)
```json
{
  "longName": "Apple Inc.",
  "industry": "Consumer Electronics",
  "sector": "Technology",
  "marketCap": 3828662403072,
  "sharesOutstanding": 14681140000
}
```

### 재무 데이터 (DataFrame 유사 형식)
```json
{
  "incomeStatement": [
    {"항목": "Total Revenue", "2025-12-31": "1.43756e+11", ...},
    ...
  ],
  "balanceSheet": [...],
  "cashFlow": [...]
}
```

### 투자보고서 (Markdown 형식)
```json
{
  "ticker": "AAPL",
  "companyName": "Apple Inc.",
  "markdownContent": "# Apple Inc. (AAPL) 분석 보고서\n\n## 1) 사업 개요와..."
}
```

## 프론트엔드 연동

Next.js 프론트엔드에서 `.env.local` 파일에 다음 환경변수 설정:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```
