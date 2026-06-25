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

MIN_ACCEPTABLE_FIT_SCORE = 30
MAX_RETRY_COUNT = 1

def route_by_fit_score(state: AgentState) -> str:
    """
    gap_analyze 이후 호출되는 라우터.
    점수가 너무 낮고 아직 재시도를 안 했으면 검색을 다시 시도하고,
    그렇지 않으면(점수가 충분하거나 이미 재시도했으면) 종료한다.

    retry_count로 재시도 한도를 두는 이유: 이게 없으면 검색을 넓혀도
    여전히 낮은 점수가 나올 때 영원히 같은 경로를 도는 무한 루프가 될 수 있다.
    """
    fit_score = state.get("fit_score", 0)
    retry_count = state.get("retry_count", 0)

    if fit_score < MIN_ACCEPTABLE_FIT_SCORE and retry_count < MAX_RETRY_COUNT:
        return "retry_search"
    return "finish"