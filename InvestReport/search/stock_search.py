from dotenv import load_dotenv
import os

load_dotenv()
MEILISEARCH_MASTER_KEY = os.environ['MEILISEARCH_MASTER_KEY']

from meilisearch import Client
client = Client("http://127.0.0.1:7700", MEILISEARCH_MASTER_KEY)

#종목 모드 검색
def stock_search(query: str):
    return client.index('nasdaq').search(query)
    
    # return client.index('nasdaq').search(
    #     query,
    #     {"attributesToSearchOn": ["symbol","name"], "matchingStrategy": "all"}
    # )
