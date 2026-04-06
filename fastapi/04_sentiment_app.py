from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
# get_hf_client
from hfi_utils import get_hf_client 
from fastapi.middleware.cors import CORSMiddleware  # 1. 미들웨어 임포트

app = FastAPI()

# 2. CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 모든 도메인에서의 접속을 허용
    allow_credentials=True,
    allow_methods=["*"],           # POST, OPTIONS 등 모든 HTTP 메서드 허용
    allow_headers=["*"],           # 모든 헤더 허용
)

# 서버 시작 시 클라이언트 초기화 (1회)
client = get_hf_client()
print("**** client:", client)

MODEL_ID = "snunlp/KR-FinBert-SC"

# classifier = pipeline(
#     "text-classification",
#     model="snunlp/KR-FinBert-SC"
# )

class TextRequest(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    text: str
    label: str
    score: float

# # Justo for test
# @app.post("/sentiment", response_model=SentimentResponse)
# def analyze_sentiment(request: TextRequest):
#     # 실제 모델 연결 전 더미 응답
#     return SentimentResponse(
#         text=request.text,
#         label="positive",
#         score=0.95
#     )


@app.post("/sentiment", response_model=SentimentResponse)
# HuggingFace Client Interface 방식
def analyze_sentiment(request: TextRequest):
    try:
        # API 호출
        results = client.text_classification(
            model=MODEL_ID,
            text=request.text
        )
        
        # print("**** results:", results) # 터미널에서 구조 확인용

        # 1. 결과가 비어있는지 확인
        if not results or not isinstance(results, list):
            raise ValueError("API로부터 올바른 응답을 받지 못했습니다.")

        # 2. 가장 높은 점수를 가진 항목 찾기 (max 함수 사용)
        # 결과 예시: [{'label': 'negative', 'score': 0.98}, {'label': 'neutral', 'score': 0.02}]
        top_result = max(results, key=lambda x: x['score'])
        
        print("-"*120) 
        
        return SentimentResponse(
            text=request.text,
            label=top_result["label"],
            score=round(top_result["score"], 4)
        )
    
    except Exception as e:
        print(f"Error 발생: {e}")
        # 에러 발생 시 상세 내용을 확인하기 위해 에러 메시지 반환
        raise HTTPException(status_code=500, detail=str(e))
    
# HuggingFace Model 방식
# def analyze_sentiment(request: TextRequest):
#     # Request and get result from Huggingface Model
#     result = classifier(request.text)[0]
#     return SentimentResponse(
#         text=request.text,
#         label=result["label"],
#         score=round(result["score"], 4)
#     )
    
    
# 후보 모델	                                    특징	                            크기
# snunlp/KR-FinBert-SC	                        한국어 금융 특화, 감성 분류 전용	중간
# monologg/koelectra-base-finetuned-sentiment	한국어 감성 분석 범용	            중간
# klue/roberta-base	                            한국어 범용, 파인튜닝 필요	        중간

# <= 추천 => snunlp/KR-FinBert-SC

# uvicorn 04_sentiment_app:app --reload --port 8004