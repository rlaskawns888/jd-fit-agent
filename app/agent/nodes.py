# 각 단계에서 실제로 하는 일

from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.services.llm_service import LLMService
from app.tools.resume_search_tool import search_resume_chunks, build_search_query_from_jd, build_broader_search_query_from_jd

# JD가 분석 가능한 수준인지 판단하는 임시 기준
# 다음 단계(LLM 연결)에서 이 숫자 기준은 LLM 판단으로 교체된다.
MIN_JD_LENGTH_FRO_ANALYSIS = 80

def collect_jd_node(state: AgentState) -> dict:
    """
    입력으로 들어온 jd_text를 그래프 상태에 들여놓는 시작 노드.
    """
    jd_text = state["jd_text"].strip()

    return {
        "jd_text": jd_text,
        "visited_nodes": state.get("visited_nodes", []) + ["collect_jd"]
    }


def assess_jd_quality_node(state: AgentState) -> dict:
    """
    JD 텍스트가 분석하기에 충분한 정보를 담고 있는지 LLM에게 판단을 맡긴다.
    """
    jd_text = state["jd_text"]

    # OpenAI
    system_prompt = (
        "너는 채용공고(JD) 품질을 평가하는 전문가다. "
        "주어진 JD 텍스트가 회사명/역할/필수기술 등 분석에 필요한 "
        "최소한의 정보를 담고 있는지 판단하라. "
        "반드시 JSON 형식으로만 답하라. "
        '형식: {"quality": "sufficient" 또는 "insufficient", "reason": "판단 이유 한 문장"}'
    )
    user_prompt = f"다음 JD 텍스트를 평가해줘:\n\n{jd_text}"

    llm = LLMService()
    result = llm.ask_json(system_prompt, user_prompt)

    quality = result.get("quality", "insufficient")
    reason = result.get("reason", "")

    return {
        "jd_quality": quality,
        "quality_reason": reason,
        "visited_nodes": state.get("visited_nodes", []) + ["assess_jd_quality"]
    }


def analyze_jd_node(state: AgentState) -> dict:
    """
    JD를 구조화 분석하는 노드. 필수기술/우대사항/도메인을 LLM으로 추출한다.
    """
    jd_text = state["jd_text"]

    system_prompt = (
        "너는 채용공고(JD) 분석 전문가다. 주어진 JD에서 핵심 정보를 추출하라. "
        "반드시 JSON 형식으로만 답하라. "
        '형식: {"company_name": "회사명 또는 Unknown", '
        '"job_title": "직무명 또는 Unknown", '
        '"required_skills": ["필수기술1", "필수기술2"], '
        '"preferred_skills": ["우대기술1", "우대기술2"], '
        '"domain": "도메인 설명 한 문장"}'
    )
    user_prompt = f"다음 JD를 분석해줘:\n\n{jd_text}"

    llm = LLMService()
    result = llm.ask_json(system_prompt, user_prompt)

    return {
        "jd_summary": result,
        "visited_nodes": state.get("visited_nodes", []) + ["analyze_jd"],
    }


def make_search_resume_node(db: Session, use_broader_query: bool = False):
    """
    search_resume_node는 db: Session이 필요한데, LangGraph 노드 함수는
    (state) 또는 (state, config) 형태만 받을 수 있다.
    그래서 db를 미리 "묻혀두고" state만 받는 함수를 만들어서 돌려주는
    팩토리 패턴을 쓴다. graph.py에서 그래프를 빌드할 때 이 함수를 호출해서
    실제 노드로 등록한다.
    """
    def search_resume_node(state: AgentState) -> dict:
        """
        JD 분석 결과(required_skills, preferred_skills)로 검색 문장을 만들고,
        이력서 chunk 중 의미적으로 가장 가까운 것들을 pgvector로 찾아온다.
        """
        jd_summary = state.get("jd_summary")

        if use_broader_query:
            #재시도
            query_text = build_broader_search_query_from_jd(jd_summary)
        else:
            query_text = build_search_query_from_jd(jd_summary)

        if not query_text:
            # JD (x) 빈결과로 놔둔다
            return {
                "matched_chunks": [],
                "visited_nodes": state.get("visited_nodes", []) + ["search_resume"],
            }
        
        matched_chunks = search_resume_chunks(
            db=db,
            query_text=query_text,
            resume_id=state.get("resume_id"),
            top_k=5
        )

        return {
            "matched_chunks": matched_chunks,
            "visited_nodes": state.get("visited_nodes", []) + ["search_resume"],
        }
    
    return search_resume_node


def increment_retry_node(state: AgentState) -> dict:
    """
    재시도 경로로 들어왔을 때 retry_count를 1 올린다.
    이 카운트가 route_by_fit_score의 종료 조건으로 쓰인다.
    """
    return {
        "retry_count": state.get("retry_count", 0) + 1,
        "visited_nodes": state.get("visited_nodes", []) + ["increment_retry"],
    }


def gap_analyze_node(state: AgentState) -> dict:
    """
    JD 요구사항(jd_summary)과 검색된 이력서 경험(matched_chunks)을 비교해서
    적합도 점수, 강점, 부족한 점을 LLM이 판단하게 한다.

    이 노드가 "Reasoning"을 가장 직접적으로 보여주는 지점이다:
    단순 추출(analyze_jd)이나 단순 검색(search_resume)과 달리,
    두 정보를 놓고 "비교해서 판단"하는 작업이 여기서 일어난다.
    """
    jd_summary = state.get("jd_summary") or {}
    matched_chunks = state.get("matched_chunks") or {}

    if not matched_chunks:
        #검색 X -> 보수적 처리 
        return {
            "fit_score": 0,
            "strengths": [],
            "gaps": jd_summary.get("required_skills", []),
            "visited_nodes": state.get("visited_nodes", []) + ["gap_analyze"],
        }
    
    experiences_text = "\n---\n".join(
        f"[경험 {i+1}] {chunk['content']}" for i, chunk in enumerate(matched_chunks)
    )

    system_prompt = (
        "너는 채용 적합도를 평가하는 심사관이다. "
        "JD 요구사항과 후보자의 실제 경험을 비교해서 적합도를 평가하라. "
        "후보자 경험에 명확히 근거가 있는 부분만 강점으로 인정하고, "
        "막연하거나 추측에 의존해야 하는 부분은 강점으로 인정하지 마라. "
        "단, JD가 요구하는 기술과 후보자의 경험이 기술 스택은 다르지만 "
        "개념적으로 동일하거나 전이 가능한 역량인 경우(예: 비동기 작업 상태 관리 경험은 "
        "Agent의 State Management와 개념적으로 연결됨), 그 연결 관계를 설명하며 "
        "강점으로 인정하라. 과장 없이 근거를 명확히 제시하라. "
        "반드시 JSON 형식으로만 답하라. "
        '형식: {"fit_score": 0부터 100 사이 정수, '
        '"strengths": ["JD 요구사항과 연결되는 실제 경험과 그 이유"], '
        '"gaps": ["JD가 요구하지만 경험에서 근거를 찾을 수 없는 부분들"]}'
    )

    user_prompt = (
        f"JD 필수기술: {jd_summary.get('required_skills', [])}\n"
        f"JD 우대사항: {jd_summary.get('preferred_skills', [])}\n"
        f"JD 도메인: {jd_summary.get('domain', '')}\n\n"
        f"후보자 경험:\n{experiences_text}\n\n"
        "위 정보를 바탕으로 적합도를 평가해줘."
    )

    llm = LLMService()
    result = llm.ask_json(system_prompt, user_prompt)

    return {
        "fit_score": result.get("fit_score", 0),
        "strengths": result.get("strengths", []),
        "gaps": result.get("gaps", []),
        "visited_nodes": state.get("visited_nodes", []) + ["gap_analyze"],
    }


def resume_feedback_node(state: AgentState) -> dict:
    """
    JD 요구사항과 갭 분석 결과를 바탕으로, 원티드 이력서 피드백 스타일의
    문장 단위 개선 제안을 만든다.

    사실 왜곡을 막기 위해, LLM에게 반드시 matched_chunks의 원문을 인용하고
    그 문장을 어떻게 고치면 좋을지만 제안하도록 강하게 지시한다.
    """
    jd_summary = state.get("jd_summary") or {}
    matched_chunks = state.get("matched_chunks") or []
    strengths = state.get("strengths") or []
    gaps = state.get("gaps") or []

    if not matched_chunks:
        return {
            "resume_feedback": None,
            "visited_nodes": state.get("visited_nodes", []) + ["resume_feedback"],
        }
    
    resume_text = "\n---\n".join(chunk["content"] for chunk in matched_chunks)

    system_prompt = (
        "너는 이력서 첨삭 전문가다. 채용공고(JD) 요구사항에 맞춰 "
        "이력서를 어떻게 개선하면 좋을지 문장 단위로 피드백하라. "
        "반드시 이력서 원문에 실제로 있는 문장만 인용해서 피드백하라. "
        "\n\n"
        "rewritten_example을 작성할 때 다음 규칙을 엄격히 지켜라: "
        "1) 원문에 등장하지 않는 기술명, 도구명, 회사명, 프레임워크명(예: Agent, RAG, GCP, "
        "OpenAI API 등)을 새로 추가하지 마라. JD에 그 기술이 요구된다고 해서 "
        "후보자가 그 기술을 썼다고 적어서는 안 된다. "
        "2) 원문에 없는 새로운 성과, 숫자, 직책, 기간을 추가하지 마라. "
        "3) 허용되는 것은 오직 '표현을 더 명확하게 다듬기', '이미 있는 사실을 "
        "JD가 쓰는 용어로 바꿔 부르기'(예: '비동기 작업 상태 추적' -> "
        "'비동기 작업의 상태 관리'), '이미 있는 사실의 강조 순서를 바꾸기' 뿐이다. "
        "4) 만약 원문 사실만으로는 JD와 명확히 연결할 표현이 없다면, "
        "rewritten_example을 원문과 동일하게 두고 suggestion에 "
        "'관련 경험을 추가로 작성해야 함'이라고 명시하라. 무리하게 연결을 지어내지 마라. "
        "\n\n"
        "반드시 JSON 형식으로만 답하라. "
        '형식: {"overall_feedback": "전체 총평 한 단락", '
        '"section_feedbacks": [{"original_text": "이력서 원문 문장", '
        '"issue": "왜 아쉬운지", '
        '"suggestion": "어떻게 고치면 좋을지 방향 설명", '
        '"rewritten_example": "원문 사실에 기반해 표현만 다듬은 예시 문장"}], '
        '"missing_keywords": ["이력서에 없지만 JD가 원하는 키워드"], '
        '"strengths_to_emphasize": ["이미 있지만 더 강조하면 좋을 부분"]}'
    )

    user_prompt = (
        f"JD 필수기술: {jd_summary.get('required_skills', [])}\n"
        f"JD 우대사항: {jd_summary.get('preferred_skills', [])}\n"
        f"이미 확인된 강점: {strengths}\n"
        f"이미 확인된 갭: {gaps}\n\n"
        f"이력서 원문:\n{resume_text}\n\n"
        "위 이력서를 JD에 맞춰 개선할 수 있도록 문장 단위로 피드백하고, "
        "각 피드백마다 표현만 다듬은 예시 문장도 같이 제시해줘. "
        "절대 원문에 없는 기술명이나 도구명을 추가하지 마."
    )

    llm = LLMService()
    result = llm.ask_json(system_prompt, user_prompt)

    return {
        "resume_feedback": result,
        "visited_nodes": state.get("visited_nodes", []) + ["resume_feedback"],
    }


def request_clarification_node(state: AgentState) -> dict:
    """
    JD 품질이 부족할 때 사용자에게 추가 정보를 요청하고 그래프를 종료하는 노드.
    """
    reason = state.get("quality_reason", "")
    message = f"JD 정보가 부족해서 분석을 진행할 수 없습니다. {reason} 회사명, 역할, 필수 기술을 포함해서 다시 입력해주세요."

    return {
        "clarification_message": message,
        "visited_nodes": state.get("visited_nodes", []) + ["request_clarification"],
    }
