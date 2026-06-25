import requests
from bs4 import BeautifulSoup

from app.core.exceptions import ApplicationError

# 채용 사이트가 봇 요청을 막는 경우가 많아서, 일반 브라우저처럼 보이는 헤더를 보낸다.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT_SECONDS = 10
MIN_EXTRACTED_TEXT_LENGTH = 50

def crawl_jd_text(jd_url: str) -> str:
    """
    JD URL에서 본문 텍스트를 추출한다.

    크롤링은 사이트마다 구조가 다르고 JS 렌더링이 필요한 경우도 많아서
    완벽히 동작하지 않을 수 있다. 실패하거나 추출된 텍스트가 너무 짧으면
    ApplicationError를 던져서, 호출하는 쪽(API)이 "jd_text로 직접 입력해달라"고
    안내할 수 있게 한다.
    """
    try:
        response = requests.get(jd_url, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ApplicationError(
            f"JD URL에 접속할 수 없습니다: {exc}. jd_text로 직접 입력해주세요.",
            status_code=422,
        ) from exc

    soup = BeautifulSoup(response.text, "html.parser")

    # script, style 태그는 텍스트가 아니라 코드이므로 제거하고 추출한다.
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    # print("DEBUG crawled text length:", len(text))
    # print("DEBUG crawled text preview:", text[:500])

    if len(text) < MIN_EXTRACTED_TEXT_LENGTH:
        raise ApplicationError(
            "JD URL에서 의미 있는 텍스트를 추출하지 못했습니다 "
            "(JavaScript 렌더링이 필요한 페이지일 수 있습니다). "
            "jd_text로 직접 입력해주세요.",
            status_code=422,
        )

    return text