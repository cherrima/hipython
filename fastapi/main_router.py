from fastapi import FastAPI
# CORS를 위한 미들웨어를 추가합니다.
from fastapi.middleware.cors import CORSMiddleware
from routers.items import router as items_router
from routers.login import router as login_router
# from routers.file_upload import router as sentiment_router
from routers.sentiment import router as sentiment_router

from pathlib import Path
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# CORS 설정: 모든 출처, 모든 메소드, 모든 헤더를 허용합니다.
# 실제 서비스에서는 보안을 위해 출처를 명시하는 것이 좋습니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items_router)
app.include_router(login_router)
app.include_router(sentiment_router)

# @app.get("/")
# def root():
#     return {"message": "Welcome to FastAPI Router Application!"}

# 1. 현재 실행 중인 파일(.py)의 부모 디렉토리 경로를 가져옵니다.
BASE_DIR = Path(__file__).resolve().parent

# 2. 'web_content' 폴더 경로를 생성합니다. ( / 연산자로 경로 연결 가능)
html_path = BASE_DIR / "web_content"

# 3. FastAPI에 연결 (문자열로 변환하여 전달하는 것이 안정적입니다)
app.mount("/", StaticFiles(directory=str(html_path), html=True), name="web")


# uvicorn main_router:app --reload --port 8001