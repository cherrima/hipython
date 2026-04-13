import streamlit as st
from rag_chain import load_rag_chain

# -----------------------------------------------
# 페이지 설정
# -----------------------------------------------
st.set_page_config(
    page_title="삼성 메모리카드 매뉴얼 챗봇",
    page_icon="📖",
    layout="centered"
)

# st.title("삼성 메모리카드 매뉴얼 챗봇")
# st.caption("매뉴얼 기반으로 정확한 답변을 제공합니다.")

# -----------------------------------------------
# 제목 및 안내문 상단 고정 (CSS 적용)
# -----------------------------------------------
# -----------------------------------------------
# 2. CSS를 이용한 상단 영역 강제 고정 (화면 분할)
# -----------------------------------------------
st.markdown("""
    <style>
        /* 상단 고정 헤더 스타일 */
        .fixed-header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: white;
            z-index: 1000;
            padding: 10px 0 10px 0;
            border-bottom: 2px solid #f0f2f6;
            text-align: center;
        }
        
        /* 헤더 높이만큼 본문 컨텐츠에 여백 추가 (겹침 방지) */
        .main .block-container {
            padding-top: 180px; 
        }

        /* Streamlit 기본 헤더 숨기기 (선택 사항) */
        [data-testid="stHeader"] {
            display: none;
        }
    </style>
    
    <div class="fixed-header">
        <h1 style="margin: 0; font-size: 24px;">📖 삼성 메모리카드 매뉴얼 챗봇</h1>
        <p style="margin: 5px 0 0 0; color: #666;">매뉴얼 기반으로 정확한 답변을 제공합니다.</p>
    </div>
""", unsafe_allow_html=True)

# header = st.container(border=True)
# header.title("삼성 메모리카드 매뉴얼 챗봇")
# header.caption("매뉴얼 기반으로 정확한 답변을 제공합니다.")


# -----------------------------------------------
# RAG 체인 초기화 (최초 1회만 실행하도록 캐싱)
# -----------------------------------------------
# manual_path = r"D:\Practice\hipython\llm\data\Samsung_Card_Manual_Korean_1.3.pdf"
# rag_chain = load_rag_chain(manual_path, model = "gpt-4o-mini")

@st.cache_resource
def get_rag_chain():
    manual_path = r"D:\Practice\hipython\llm\data\Samsung_Card_Manual_Korean_1.3.pdf"
    return load_rag_chain(manual_path, model="gpt-4o-mini")

rag_chain = get_rag_chain()

# -----------------------------------------------
# 대화 히스토리 초기화
# -----------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------
# 이전 대화 출력
# -----------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------
# 사용자 입력 처리
# -----------------------------------------------
# chat_input은 화면 하단에 고정된 입력창을 생성합니다.
if user_query := st.chat_input("질문을 입력하세요"):
    
    # 1. 사용자 질문 출력 및 히스토리 저장
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # 2. RAG 체인을 통한 답변 생성 및 출력
    with st.chat_message("assistant"):
        # load_rag_chain이 체인 객체를 반환한다면 .invoke() 등을 사용해야 합니다.
        # 여기서는 구성된 rag_chain에 쿼리를 전달하는 일반적인 형식을 가정합니다.
        response = rag_chain.invoke(user_query) 
        
        # 답변 결과가 문자열이 아닌 객체라면 적절한 필드(예: response.content)를 추출하세요.
        answer = response if isinstance(response, str) else response.get('answer', response)
        
        st.markdown(answer)
    
    # 3. 답변 히스토리 저장
    st.session_state.messages.append({"role": "assistant", "content": answer})
    
#streamlit run chatbot_app.py