# 01_simple_agent.py

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent   # LangChain 1.x
# from langgraph.prebuilt import create_react_agent

# LLM 정의
llm = ChatOpenAI(model="gpt-4o-mini")

# 1. 도구 정의
@tool
def add(a: float, b: float) -> float:
    """두 숫자를 더합니다."""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """두 숫자를 곱합니다."""
    return a * b

tools = [add, multiply]

# 2. 에이전트 생성
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="당신은 계산을 도와주는 어시스턴트입니다."
)

# 3. 실행
result = agent.invoke({
    "messages": [{"role": "user", "content": "3 더하기 5는 얼마야? 그리고 그 결과에 7을 곱하면?"}]
})

print(result["messages"][-1].content)