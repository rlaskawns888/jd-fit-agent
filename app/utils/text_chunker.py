def split_into_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    긴 텍스트를 chunk_size 글자 단위로 자르되, overlap 만큼 겹치게 쪼갠다.

    겹치게 자르는 이유: 문장이 chunk 경계에서 끊기면 그 경계에 걸친 의미가
    양쪽 chunk 모두에서 어색하게 잘릴 수 있다. overlap을 주면 경계 부분의
    맥락이 양쪽 chunk에 일부 중복으로 남아서 검색 품질이 좋아진다.
    """
    text = text.strip()
    if not text:
        return []
    
    if chunk_size <= overlap:
        raise ValueError("chunk_size는 overlap보다 커야 합니다.")
    
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(text[start:end])

        if end == text_length:
            break

        start = end - overlap

    return chunks
