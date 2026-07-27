import sys, os, json
from datetime import datetime, timedelta

CODESET_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CODESET_DIR not in sys.path:
    sys.path.append(CODESET_DIR)

from dotenv import load_dotenv
from opensearchpy import AsyncOpenSearch
import httpx
from openai import AsyncOpenAI

current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.abspath(os.path.join(current_dir, "..", "..", "dataset", "config", ".env"))
load_dotenv(dotenv_path=dotenv_path, override=True)

OS_HOST = os.getenv("OS_HOST", "localhost")
OS_PORT = int(os.getenv("OS_PORT", 9200))
OS_USER = os.getenv("OS_USER", "admin")
OS_PASSWORD = os.getenv("OS_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 최종 답변 생성용

INDEX_NAME = "news_stock_sentiment"

os_client = AsyncOpenSearch(
    hosts=[{"host": OS_HOST, "port": OS_PORT}],
    http_auth=(OS_USER, OS_PASSWORD),
    use_ssl=True, verify_certs=False, ssl_show_warn=False,
)

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# 워치리스트 필터에서 실제 존재하는 sector 값들 (LLM이 뽑은 자유 텍스트 기준)
KNOWN_SECTORS = ["반도체", "전기·전자", "기계·장비", "통신업", "서비스업"]


## ======================= 질의에서 섹터 추출 (하드코딩 파서, MVP) =======================
def extract_sector_from_message(message: str) -> str:
    for sector in KNOWN_SECTORS:
        if sector in message:
            return sector
    if "ai" in message.lower() or "인공지능" in message:
        return "반도체"  # AI 관련 질의는 일단 반도체로 매핑 (스코프 안이 대부분 반도체라)
    return "반도체"  # 기본값


## ======================= 질문 임베딩 (비동기) =======================
async def get_query_embedding(text: str):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "http://localhost:11434/api/embeddings",
            json={"model": "bge-m3", "prompt": text},
            timeout=30.0
        )
        return res.json()["embedding"]


## ======================= 하이브리드 검색 =======================
async def search_sector_news(sector: str, hours: int = 24, size: int = 10):
    time_from = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S")

    query = {
        "query": {
            "bool": {
                "filter": [
                    {"term": {"sector": sector}},
                    {"term": {"sentiment": "positive"}},
                    {"range": {"published_at": {"gte": time_from}}}
                ]
            }
        },
        "sort": [{"importance": {"order": "desc"}}],
        "size": size
    }

    res = await os_client.search(index=INDEX_NAME, body=query)
    return [hit["_source"] for hit in res["hits"]["hits"]]


## ======================= 종목별 그룹핑 =======================
def group_by_stock(articles: list) -> dict:
    grouped = {}
    for art in articles:
        key = art["matched_name"]
        grouped.setdefault(key, []).append(art)
    return grouped


## ======================= 최종 답변 생성 프롬프트 조립 =======================
def build_answer_prompt(sector: str, grouped: dict, chat_summary: str) -> str:
    context_lines = []
    for stock_name, articles in grouped.items():
        for art in articles[:2]:  # 종목당 최대 2개 기사만 근거로
            url = art.get("source_url") or ""
            if not url.strip():
                continue  # URL 없는 근거는 컨텍스트에서 제외 (환각 방지)
            context_lines.append(
                f"- [{stock_name}] {art['summary']} (출처: {art['source']} | {url})"
            )

    context_text = "\n".join(context_lines)

    prompt = f"""너는 한국 주식 뉴스 기반 섹터 추천 어시스턴트다.
        이전 대화 요약: {chat_summary or '없음'}
    
        다음은 '{sector}' 섹터의 최근 24시간 호재성 뉴스 근거자료다:
        {context_text}
    
        위 근거를 바탕으로 어떤 종목들이 호재 요인을 가지고 있는지 한국어로 간결하게 설명해라.
    
        출력 형식 규칙 (반드시 지켜라):
        - 각 종목 설명 뒤에는 반드시 줄바꿈을 넣어라.
        - 출처는 반드시 마크다운 링크 문법 [출처](URL) 형식으로만 표기해라. URL을 텍스트로 그대로 노출하지 마라.
        - 제공되지 않은 URL은 절대 만들어내지 마라.
    
        예시:
        삼성전자는 메모리 가격 상승 기대감으로 강세가 예상됩니다. [출처](https://example.com/news/1)
    """
    return prompt


## ======================= 스트리밍 답변 생성 =======================
async def generate_answer_stream(prompt: str):
    stream = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


## ======================= 대화 요약 압축 (Redis용) =======================
async def summarize_old_turns(old_turns: list, existing_summary: str) -> str:
    turns_text = "\n".join([f"{t['role']}: {t['content']}" for t in old_turns])
    prompt = f"기존 요약: {existing_summary}\n\n새 대화:\n{turns_text}\n\n위 내용을 반영해 대화 맥락을 3문장 이내로 요약해줘."

    res = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content