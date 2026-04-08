# routers/items.py

from fastapi import APIRouter

router = APIRouter(prefix="/items", tags=["품목"])

# 임시 종목 데이터
COMPUTER_ITEMS = [
    {"item_id": 1, "name": "데스크탑"},
    {"item_id": 2, "name": "워크스테이션"},
    {"item_id": 3, "name": "중형서버"},
    {"item_id": 4, "name": "대형서버"},
    {"item_id": 5, "name": "슈퍼컴퓨터"},
]


@router.get("/")
def list_items():
    return COMPUTER_ITEMS


@router.get("/{item_id}")
def read_item(item_id: int) -> dict: 
    
    item_name = "대상없음"
    # 아이템 이름 가져오기
    for item in COMPUTER_ITEMS :
        if ( item["item_id"] == item_id ):
           item_name =  item["name"]
           break ;

    return {"name": item_name}

