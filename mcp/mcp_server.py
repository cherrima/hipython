from fastmcp import FastMCP
from dotenv import load_dotenv
from notion_client import Client
import json
import os

load_dotenv(r"D:\Practice\hipython\llm\.env", override=True)

mcp = FastMCP("ExperimentResultServer")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
notion = Client(auth=NOTION_TOKEN)


@mcp.tool()  # 함수를 tool로 정의
def read_experiment_result(file_path: str) -> str:
    """
    모델 학습 결과 JSON 파일을 읽어 문자열로 반환합니다.
    file_path: JSON 파일 경로 (예: train_result.json)
    """
    if not os.path.exists(file_path):
        return f"[ERROR] 파일을 찾을 수 없습니다: {file_path}"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"[ERROR] 파일 읽기 실패: {str(e)}"


@mcp.tool() # 함수를 tool로 정의
def upload_experiment_to_notion(title: str, summary: str) -> str:
    """
    제목이 동일한 페이지가 있으면 내용을 교체하고, 없으면 신규 생성합니다.
    """
    if not NOTION_PAGE_ID:
        return "[ERROR] NOTION_PAGE_ID가 설정되지 않았습니다."

    try:
        # 1. 동일한 제목의 페이지가 있는지 검색
        search_results = notion.search(
            query=title,
            filter={"property": "object", "value": "page"}
        ).get("results", [])

        # 정확히 제목이 일치하는 페이지 찾기
        existing_page = None
        for page in search_results:
            # 제목 속성 추출 (보통 'title' 또는 데이터베이스인 경우 'Name' 등 확인 필요)
            properties = page.get("properties", {})
            page_title_list = properties.get("title", {}).get("title", [])
            if page_title_list and page_title_list[0].get("plain_text") == title:
                existing_page = page
                break

        # 본문 내용 정의 (공통으로 사용)
        new_content = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": summary}}]
                }
            }
        ]

        if existing_page:
            page_id = existing_page["id"]
            
            # 2. 기존 페이지의 본문(children) 업데이트
            # Notion API 특성상 기존 블록을 다 지우고 새로 넣거나, 
            # 단순히 아래에 추가하는 방식이 일반적입니다. 여기서는 '교체'를 위해 기존 블록을 확인합니다.
            blocks = notion.blocks.children.list(block_id=page_id).get("results", [])
            
            # 기존 블록 삭제 (진정한 '교체'를 위해)
            for block in blocks:
                notion.blocks.delete(block_id=block["id"])
            
            # 새로운 본문 추가
            notion.blocks.children.append(block_id=page_id, children=new_content)
            
            page_url = existing_page.get("url", "URL 없음")
            return f"기존 Notion 페이지 교체 완료: {page_url}"

        else:
            # 3. 신규 페이지 생성 (기존 로직)
            response = notion.pages.create(
                parent={"page_id": NOTION_PAGE_ID},
                properties={
                    "title": {"title": [{"text": {"content": title}}]}
                },
                children=new_content
            )
            page_url = response.get("url", "URL 없음")
            return f"신규 Notion 페이지 생성 완료: {page_url}"

    except Exception as e:
        return f"[ERROR] Notion 처리 실패: {str(e)}"



if __name__ == "__main__":
    print("MCP Server 실행 중...")
    mcp.run(transport="stdio")