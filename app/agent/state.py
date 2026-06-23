# 그래프가 들고 다니는 "상태" 정의

from typing import Any, Optional, TypedDict

class AgentState(TypedDict):
    """
    LangGraph가 노드 사이를 이동할 때 들고 다니는 상태.

    TypedDict를 쓰는 이유: 각 노드는 이 state의 일부만 읽고/갱신하는데,
    dict라서 "이번 노드가 추가한 필드"만 리턴해도 LangGraph가 기존 state와
    합쳐준다 (전체를 매번 다시 만들 필요가 없음).
    """

    #입력   
    jd_text: str #사용자가 입력한 JD원문
    resume_id: Optional[str]

    #assess_jd_quality_node가 채우는 값
    jd_quality: Optional[str] # "sufficient" | "insufficient"
    quality_reason: Optional[str]  # 왜 그렇게 판단했는지 (디버깅/설명용)

    #analyze_jd_node가 채우는 값 (지금 단계는 mock)
    jd_summary: Optional[dict[str, Any]]

    #request_clarification_node가 채우는 값
    clarification_message: Optional[str] #설명 요청 메시지

    # --- 그래프 전체를 거치며 어떤 노드를 지나왔는지 기록 ---
    # "에이전트가 실제로 어떤 경로를 선택했는지" 보여줄 수 있는 핵심 필드라서 처음부터 넣어둔다.
    visited_nodes: list[str]