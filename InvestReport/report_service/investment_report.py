#종목 투자보고서 프롬프트 실행

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers  import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

chat_template = ChatPromptTemplate.from_messages([
    ("system", """Want assistance provided by qualified individuals enabled with experience on understanding charts using technical analysis tools while interpreting macroeconomic environment prevailing across world consequently assisting customers acquire long term advantages requires clear verdicts therefore seeking same through informed predictions written down precisely! First statement contains following content- 'Can you tell us what future stock market looks like based upon current conditions ?'"""),
    ("human", """회사: {company}

                [기본정보]
                {basic_info}

                [분기 재무]
                {financials}

                요구사항:
                1) 사업 개요와 최근 분기 핵심 포인트 3가지
                2) 실적 추세(매출/영업이익/순이익) 요약
                3) 리스크 2가지, 모멘텀 2가지
                4) 투자 아이디어와 관찰지표 체크리스트
                5) 10줄 요약
                출력은 마크다운으로 작성"""
    )
])

chain = chat_template | llm | StrOutputParser()

def investment_report(company: str, basic_info: str, financials: str) -> str:
    
    # 1. chat_template에 변수를 주입하여 메시지 객체 생성
    # format_messages나 invoke를 사용합니다.
    prompt_params = {
        "company": company,
        "basic_info": basic_info,
        "financials": financials
    }
    
    # 2. llm에 완성된 prompt_value를 전달
    return chain.invoke(prompt_params)


