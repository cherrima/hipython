from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


def load_rag_chain(pdf_path: str, model: str = "gpt-4o-mini"):
    # 1. PDF 로딩
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()  # List[Document] 형태로 반환

    # 2. 텍스트 분할
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = splitter.split_documents(pages)

    # 3. 임베딩 + 벡터 DB
    load_dotenv()
    embeddings = OpenAIEmbeddings()
    
    vectordb = FAISS.from_documents(docs, embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    # k는 반환할 청크 수입니다. 도메인과 청크 크기에 따라 조정합니다.

    # 4. 프롬프트
    prompt = ChatPromptTemplate.from_template("""
        너는 삼성전자 메모리카드 매뉴얼 전문 어시스턴트이다.
        다음의 참고 문서를 바탕으로 질문에 정확하게 답하라.

        [참고문서]
        {context}

        [질문]
        {question}

        한글로 간결하고 정확하게 답변하라. 
    """)

    # 5. RAG 체인
    llm = ChatOpenAI(model=model)
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain
