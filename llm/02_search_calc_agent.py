# 02_search_calc_agent.py

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_tavily import TavilySearch       # langchain-tavily 패키지
from langchain.agents import create_agent
import ast
import operator

# 1. 도구 정의: 웹 검색
search_tool = TavilySearch(max_results=3)

# 2. 도구 정의: 안전한 계산기
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}

def _safe_eval(node):
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        op = SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"지원하지 않는 연산자: {node.op}")
        return op(_safe_eval(node.left), _safe_eval(node.right))
    raise ValueError(f"허용되지 않는 표현식: {node}")

@tool
def calculate(expression: str) -> str:
    """사칙연산과 거듭제곱만 허용하는 안전한 계산기입니다. 예: '1234 * 5678'"""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return str(result)
    except Exception as e:
        return f"계산 오류: {e}"

# 3. 에이전트 생성
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent = create_agent(
    model=llm,
    tools=[search_tool, calculate],
    prompt="""당신은 웹 검색과 계산을 도와주는 AI 어시스턴트입니다.

규칙:
- 동일하거나 유사한 검색 쿼리를 반복하지 마세요.
- 검색 결과가 없으면 즉시 그 사실을 사용자에게 알리세요.
- 최대 3번 검색 후 반드시 최종 답변을 제공하세요.""",
)

# 4. 테스트 실행
print("=== 테스트 1: 검색만 사용 ===")
result1 = agent.invoke({
    "messages": [{"role": "user", "content": "2024년 한국 GDP는 얼마야?"}]
})
print(result1["messages"][-1].content)

print("\n=== 테스트 2: 계산기만 사용 ===")
result2 = agent.invoke({
    "messages": [{"role": "user", "content": "1234 곱하기 5678은 얼마야?"}]
})
print(result2["messages"][-1].content)

print("\n=== 테스트 3: 검색 + 계산기 모두 사용 ===")
result3 = agent.invoke({
    "messages": [{"role": "user", "content": "2024년 한국 GDP를 검색하고, 그 금액을 1300으로 나누면 얼마야?"}]
})
print(result3["messages"][-1].content)