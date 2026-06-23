import json

from openai import OpenAI

from app.core.config import settings
from app.core.exceptions import ApplicationError

class LLMService:
    """
    OpenAI Chat Completions를 감싸는 공용 서비스.
    여러 노드(JD 품질 판단, JD 분석, 이후 갭 분석 등)가
    이 클래스를 통해서만 LLM을 호출하게 만들어 호출 방식을 한 곳에서 관리한다.
    """

    def __init__(self):
        if not settings.openai_api_key:
            raise ApplicationError("OPEN_API_KEY (x)", status_code=500)
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
    
    def ask_json(self, system_prompt: str, user_prompt: str) -> dict:
        """
        LLM에게 질문하고 JSON 객체로만 답을 받는다.

        주의: OpenAI는 response_format=json_object를 쓸 때 system 또는 user
        메시지 어딘가에 반드시 "JSON"이라는 단어가 포함되어야 한다는 제약이 있다.
        (없으면 400 에러가 난다.) 그래서 system_prompt를 짤 때 항상
        "JSON 형식으로 답하라"는 지시를 포함해야 한다.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise ApplicationError(
                f"LLM 응답이 올바른 JSON 형식이 아닙니다: {content}",
                status_code=502,
            ) from exc