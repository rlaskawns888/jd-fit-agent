# 각 단계에서 실제로 하는 일

from app.agent.state import AgentState

# JD가 분석 가능한 수준인지 판단하는 임시 기준
# 다음 단계(LLM 연결)에서 이 숫자 기준은 LLM 판단으로 교체된다.
MIN_JD_LENGTH_FRO_ANALYSIS = 80

def collect_jd_node(state: AgentState) -> dict:
    """
    입력으로 들어온 jd_text를 그래프 상태에 들여놓는 시작 노드.
    지금은 텍스트를 그대로 받기만 하지만, 이후 단계에서
    jd_url 크롤링 결과를 여기로 합치게 될 자리.
    """
    jd_text = state["jd_text"].strip()

    return {
        "jd_text": jd_text,
        "visited_nodes": state.get("visited_nodes", []) + ["collect_jd"]
    }

def assess_jd_quality_node(state: AgentState) -> dict:
    """
    JD 텍스트가 분석하기에 충분한 정보를 담고 있는지 판단한다.
    이 노드의 판단 결과(jd_quality)가 다음에 어느 노드로 갈지를 결정한다.
    -> 이게 "Reasoning이 그래프의 흐름 자체를 바꾸는" 지점.

    지금은 텍스트 길이로만 판단하는 mock 버전.
    다음 단계에서 LLM 호출로 교체할 때도 이 노드의 인터페이스
    (입력: state, 출력: jd_quality/quality_reason)는 그대로 유지된다.
    """
    jd_text = state["jd_text"]

    if len(jd_text) < MIN_JD_LENGTH_FRO_ANALYSIS:
        quality = "insufficient"
        reason = f"JD 텍스트가 {len(jd_text)}자로 너무 짧아 분석에 필요한 정보가 부족합니다"
    else:
        quality = "sufficient"
        reason = f"JD 텍스트가 {len(jd_text)}자로 분석 가능한 분량입니다."

    return {
        "jd_quality": quality,
        "quality_reason": reason,
        "visited_nodes": state.get("visited_nodes", []) + ["assess_jd_quality"]
    }

def analyze_jd_node(state: AgentState) -> dict:
    """
    JD를 구조화 분석하는 노드. 지금은 mock 요약만 만든다.
    다음 단계에서 OpenAI 호출로 교체되어 실제 필수기술/우대사항/도메인을 추출한다.
    """
    jd_text = state["jd_text"]
    mock_summary = f"[MOCK] 길이 {len(jd_text)}자 JD 분석 완료"

    return {
        "jd_summary": mock_summary,
        "visited_nodes": state.get("visited_nodes", []) + ["analyze_jd"],
    }

def request_clarification_node(state: AgentState) -> dict:
    """
    JD 품질이 부족할 때 사용자에게 추가 정보를 요청하고 그래프를 종료하는 노드.
    이게 State management가 필요한 이유를 보여주는 지점:
    여기서 멈춘 상태(jd_quality=insufficient)를 기억해두면,
    이후 단계에서 사용자가 보완 정보를 보냈을 때 처음부터 다시 묻지 않고
    이어서 분석할 수 있다.
    """
    reason = state.get("quality_reason", "")
    message = f"JD 정보가 부족해서 분석을 진행할 수 없습니다. {reason} 회사명, 역할, 필수 기술을 포함해서 다시 입력해주세요."

    return {
        "clarification_message": message,
        "visited_nodes": state.get("visited_nodes", []) + ["request_clarification"],
    }
