from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from s3_client import s3, BUCKET_NAME
import os, uuid, httpx
import urllib.parse  # 한글 파일명 처리를 위한 라이브러리
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 환경 변수 (예: 'dev' 또는 'prod')
# 실행 시: SET ENV=dev (Windows) 또는 export ENV=dev (Linux/Mac)
PHASE = os.getenv("ENV", "dev").strip()  # ENV 변수가 정의되어 있지 않으면 "dev"로 지정

INDEX_HTML_URL   = "https://dev-insta-uploaded-files-05.s3.ap-northeast-2.amazonaws.com/index.html"
INDEX_HTML_LOCAL = "./web-content/index.html" # 로컬 index.html 경로

# CORS 설정: S3 URL로부터 오는 요청을 허용합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        INDEX_HTML_URL,
        "http://localhost:3000", # 로컬 개발용 테스트 시
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"], # 모든 HTTP 메서드 허용 (GET, POST 등)
    allow_headers=["*"], # 모든 헤더 허용
)


# @app.get("/") 
# async def proxy_root():
    
#     TARGET_URL = "http://dev-insta-uploaded-files-05.s3-website.ap-northeast-2.amazonaws.com/"
#     async with httpx.AsyncClient() as client:
#         # FastAPI 서버가 S3 URL을 직접 호출합니다.
#         response = await client.get(TARGET_URL)
        
#         # S3로부터 받은 결과(HTML 등)를 브라우저에 그대로 전달합니다.
#         # 이 과정을 통해 브라우저의 URL은 변경되지 않고 유지됩니다.
#         return Response(
#             content=response.content,
#             status_code=response.status_code,
#             media_type=response.headers.get("Content-Type")
#         )



# 환경 정보 제공
@app.get("/env")
async def get_env():
    # PHASE = os.getenv("ENV", "dev").strip()
    # 환경 정보만 짧게 응답
    return {"phase": PHASE}

# root - index.html
@app.get("/")
async def read_root():
    print(f"PHASE: [{PHASE}]")
    if PHASE == "prod":
        async with httpx.AsyncClient() as client:
            response = await client.get(INDEX_HTML_URL)
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="S3 Index Not Found")
            return HTMLResponse(content=response.text)
    else:
        return FileResponse(INDEX_HTML_LOCAL)

# @app.get("/", response_class=HTMLResponse)
# async def read_root():
#     async with httpx.AsyncClient() as client:
#         # 1. 외부 S3에서 index.html 내용을 읽어옵니다.
#         response = await client.get(INDEX_HTML_URL)
        
#         # 2. 읽어온 HTML 내용을 그대로 브라우저에 응답합니다.
#         # 이 방식을 사용하면 브라우저 주소창의 URL은 변하지 않습니다.
#         return HTMLResponse(content=response.text, status_code=response.status_code)

# 이미지 업로드 - 기존  : 파일명 익명화
# @app.post("/images")
# async def upload_image(file: UploadFile = File(...)):
#     ext = file.filename.split(".")[-1]
#     key = f"{uuid.uuid4()}.{ext}"

#     try:
#         s3.upload_fileobj(
#             file.file,
#             BUCKET_NAME,
#             key,
#             ExtraArgs={"ContentType": file.content_type},
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

#     url = f"https://{BUCKET_NAME}.s3.ap-southeast-2.amazonaws.com/{key}"
#     return {"filename": key, "url": url}


# 이미지 업로드 - 기존  : 파일명 보존
@app.post("/images")
async def upload_image(file: UploadFile = File(...)):
    # 1. 원래 파일명 그대로 사용 (경로 조작 방지를 위해 basename 처리)
    filename = os.path.basename(file.filename)
    
    # S3 키(파일명) 설정
    key = filename

    try:
        s3.upload_fileobj(
            file.file,
            BUCKET_NAME,
            key,
            ExtraArgs={
                "ContentType": file.content_type,
                # 한글 파일명이 깨지지 않도록 메타데이터 설정 (선택사항)
                "ContentDisposition": f"inline; filename*=UTF-8''{urllib.parse.quote(filename)}"
            },
        )
    except Exception as e:
        print(f"❌ S3 업로드 에러: {e}")
        raise HTTPException(status_code=500, detail=f"S3 업로드 실패: {str(e)}")

    # 주의: BUCKET_NAME 및 리전 정보를 확인하세요 (제공해주신 URL 구조 유지)
    url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{key}"
    return {"filename": key, "url": url}


# 이미지 목록 조회
@app.get("/images")
def list_images():
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    objects = response.get("Contents", [])

    images = [
        {
            "filename": obj["Key"],
            "url": f"https://{BUCKET_NAME}.s3.ap-southeast-2.amazonaws.com/{obj['Key']}",
            "size": obj["Size"],
            "last_modified": str(obj["LastModified"]),
        }
        for obj in objects
    ]
    return {"count": len(images), "images": images}


# 이미지 삭제
@app.delete("/images/{filename}")
def delete_image(filename: str):
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"{filename} 삭제 완료"}