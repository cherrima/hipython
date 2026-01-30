from openai import OpenAI
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv() 

# 헬퍼 : 질의
def query_helper(role, text):
    return {
       "role": role,
        "content": [{"type":"input_text","text": text}]
    }

# 환경변수에서 API 키 읽어 클라이언트 생성
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        # {"role" : "system", "content" : "너는 광고 전문가다."},
        # {"role" : "user", "content" : "1인 컨설팅 기업에 대한 광고 문구 만들어줘."}

        query_helper("system","너는 광고 전문가다."),
        query_helper("user","1인 컨설팅 기업에 대한 광고 문구 만들어줘.")
    ],
    temperature=0
)

# temperature : 낮은 값 (0에 가까울수록): 모델이 더 결정적이고(deterministic) 일관된 응답
#               높은 값 (2에 가까울수록): 모델이 더 무작위적이고 창의적인 응답을 생성

print(response.output_text)