import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient


def get_hf_client() :

    load_dotenv() # .env 파일을 읽어와 환경 변수로 등록

    client = InferenceClient(
        provider="hf-inference",
        api_key=os.environ["HUGGINGFACE_API_KEY"],
    )
    
    return client