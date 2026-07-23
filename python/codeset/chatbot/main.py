import sys, os
CODESET_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CODESET_DIR not in sys.path:
    sys.path.append(CODESET_DIR)

from fastapi import FastAPI
from fastapi.responses import StreamingResponse  # SSE(스트리밍 응답)를 만들기 위한 FastAPI 도구
from pydantic import BaseModel  # 요청 body의 형식을 정의(검증)하는 용도

# 우리가 만든 로직들을 가져옴
from chatbot.chat_service import (
    extract_sector_from_message, search_sector_news, group_by_stock,
    build_answer_prompt, generate_answer_stream, summarize_old_turns
)
from chatbot.redis_session import get_session, append_turn

app = FastAPI()  # FastAPI 앱 인스턴스 - 이게 실제 서버 역할


# 클라이언트가 보낼 요청 body 형식 정의 - {"session_id": "...", "message": "..."} 형태만 허용
class ChatRequest(BaseModel):
    session_id: str  # 사용자(대화)를 구분하는 ID - 프론트에서 매번 같은 값 보내야 대화가 이어짐
    message: str      # 사용자가 입력한 질문


@app.post("/chat")  # POST /chat 으로 요청 오면 이 함수가 처리
async def chat(req: ChatRequest):
    # 1. 이 세션의 이전 대화 요약/최근턴 가져오기 (Redis)
    session = await get_session(req.session_id)

    # 2. 사용자 메시지에서 어떤 섹터를 물어본 건지 파악
    sector = extract_sector_from_message(req.message)

    # 3. OpenSearch에서 해당 섹터의 최근 24시간 호재 뉴스 검색
    articles = await search_sector_news(sector=sector, hours=24)

    # 4. 종목별로 묶기
    grouped = group_by_stock(articles)

    # 5. 검색결과 + 이전 대화 요약을 합쳐서 LLM한테 줄 프롬프트 완성
    prompt = build_answer_prompt(sector, grouped, session["summary"])

    # 6. 실제 스트리밍 응답을 만드는 내부 함수
    async def event_stream():
        full_answer = ""  # 나중에 Redis에 저장하려고 전체 답변을 계속 이어붙여둠
        async for delta in generate_answer_stream(prompt):
            full_answer += delta
            # SSE 규격: "data: 내용\n\n" 형태로 한 조각씩 클라이언트에 전송
            yield f"data: {delta}\n\n"

        # 답변이 다 끝나면, 이번 대화를 Redis 세션에 기록 (다음 질문에 이어서 쓸 수 있게)
        await append_turn(req.session_id, req.message, full_answer, summarize_old_turns)
        yield "data: [DONE]\n\n"  # 프론트에게 "이제 끝났다"고 알리는 신호

    # StreamingResponse: FastAPI가 이 generator를 하나씩 실행하면서 그때그때 클라이언트로 흘려보냄+ utf-8인코딩 강제
    return StreamingResponse(event_stream(), media_type="text/event-stream; charset=utf-8")