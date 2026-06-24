# 각 단계에서 실제로 하는 일

from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.services.llm_service import LLMService
from app.tools.resume_search_tool import search_resume_chunks, build_search_query_from_jd

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

    # if len(jd_text) < MIN_JD_LENGTH_FRO_ANALYSIS:
    #     quality = "insufficient"
    #     reason = f"JD 텍스트가 {len(jd_text)}자로 너무 짧아 분석에 필요한 정보가 부족합니다"
    # else:
    #     quality = "sufficient"
    #     reason = f"JD 텍스트가 {len(jd_text)}자로 분석 가능한 분량입니다."

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
    # mock_summary = f"[MOCK] 길이 {len(jd_text)}자 JD 분석 완료"

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
        # "jd_summary": mock_summary,
        "jd_summary": result,
        "visited_nodes": state.get("visited_nodes", []) + ["analyze_jd"],
    }

def make_search_resume_node(db: Session):
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
        query_text = build_search_query_from_jd(jd_summary)

        # print("DEBUG query_text:", repr(query_text))
        # print("DEBUG resume_id from state:", repr(state.get("resume_id")))

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
