# routers/file_upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from transformers import pipeline

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


router = APIRouter(prefix="/analysis", tags=["감성분석"])

# 모델 로드 (서버 시작 시 1회만 실행)
classifier = pipeline(
    "text-classification",
    model="snunlp/KR-FinBert-SC"
)


# @router.post("/sentiment")
# async def upload_sentiment(file: UploadFile = File()):
#     if file.content_type not in ["text/plain"]:
#         raise HTTPException(
#             status_code=400,
#             detail="텍스트 파일(.txt)만 업로드 가능합니다"
#         )
#     contents = await file.read()
#     text = contents.decode("utf-8")
#     result = classifier(text)[0]
#     return {
#         "filename": file.filename,
#         "text": text,
#         "label": result["label"],
#         "score": round(result["score"], 4)
#     }
    
@router.post("/sentiment")
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