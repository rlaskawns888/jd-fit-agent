#조건 분기 시 다음 노드를 결정하는 함수

from app.agent.state import AgentState

def route_by_jd_quality(state: AgentState) -> str:
    """
    LangGraph의 conditional edge에 연결되는 라우팅 함수.

    일반 노드(nodes.py)는 state를 갱신하는 dict를 리턴하지만,
    라우팅 함수는 "다음에 어느 노드 이름으로 갈지"를 문자열로 리턴한다.
    이 문자열은 graph.py에서 add_conditional_edges에 등록한 매핑 키와 일치해야 한다.
    """
    if state["jd_quality"] == "sufficient":
        return "analyze_jd"
    return "request_clarification"
