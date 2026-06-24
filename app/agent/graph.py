#노드들을 어떤 순서/조건으로 연결할지

from sqlalchemy.orm import Session

from langgraph.graph import StateGraph, START, END

from app.agent.state import AgentState
from app.agent.nodes import (
    collect_jd_node,
    assess_jd_quality_node,
    analyze_jd_node,
    make_search_resume_node,
    request_clarification_node,
)
from app.agent.router import route_by_jd_quality


def build_jd_fit_graph(db : Session):
    """
    JD Fit Agent의 LangGraph 그래프를 만들고 컴파일해서 반환한다.

    그래프 모양:
        START
          -> collect_jd
          -> assess_jd_quality
               -[sufficient]-> analyze_jd -> END
               -[insufficient]-> request_clarification -> END
    """
    builder = StateGraph(AgentState)

    builder.add_node("collect_jd", collect_jd_node)
    builder.add_node("assess_jd_quality", assess_jd_quality_node)
    builder.add_node("analyze_jd", analyze_jd_node)
    builder.add_node("search_resume", make_search_resume_node(db))
    builder.add_node("request_clarification", request_clarification_node)

    builder.add_edge(START, "collect_jd")
    builder.add_edge("collect_jd", "assess_jd_quality")

    # 조건 분기: assess_jd_quality_node가 채운 state["jd_quality"] 값에 따라
    # route_by_jd_quality가 다음 노드 이름을 결정한다.
    builder.add_conditional_edges(
        "assess_jd_quality",
        route_by_jd_quality,
        {
            "analyze_jd": "analyze_jd",
            "request_clarification": "request_clarification",
        }
    )

    builder.add_edge("analyze_jd", "search_resume")
    builder.add_edge("search_resume", END)
    builder.add_edge("request_clarification", END)

    return builder.compile()

# 그래프는 한 번만 컴파일해서 재사용한다 (요청마다 새로 빌드할 필요 없음) > 매요청 마다 그때의 DB 세션으로 새로 빌드
# jd_fit_graph = build_jd_fit_graph()
