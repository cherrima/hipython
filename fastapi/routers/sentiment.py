from fastapi import APIRouter, UploadFile, File, HTTPException
from transformers import pipeline
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

def get_hf_client() :

    load_dotenv(r"D:\Practice\hipython\fastapi\.env") # .env 파일을 읽어와 환경 변수로 등록
    
    # print("******", len(os.environ["HUGGINGFACE_API_KEY"]))

    client = InferenceClient(
        provider="hf-inference",
        api_key=os.environ["HUGGINGFACE_API_KEY"],
    )
    
    return client

router = APIRouter(prefix="/sentiment", tags=["뉴스감성분석"])

class TextRequest(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    text: str
    label: str
    score: float

@router.post("/text", response_model=SentimentResponse)
# HuggingFace Client Interface 방식
async def analyze_sentiment(request: TextRequest):
    try:
        
        client = get_hf_client()
        
        # API 호출
        results = client.text_classification(
            model="snunlp/KR-FinBert-SC",
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
    
@router.post("/file")
async def upload_sentiment(file: UploadFile = File()):
    if file.content_type not in ["text/plain"]:
        raise HTTPException(
            status_code=400,
            detail="텍스트 파일(.txt)만 업로드 가능합니다"
        )
    contents = await file.read()
    text = contents.decode("utf-8")[:512]  # 사이즈 제한
    
    client = get_hf_client()
    
    # API 호출
    results = client.text_classification(
        model="snunlp/KR-FinBert-SC",
        text=text
    )
    
    result = results[0]
    
    return {
        "filename": file.filename,
        "text": text,
        "label": result["label"],
        "score": round(result["score"], 4)
    }