import redis.asyncio as aioredis  # redis-async비동기 위해
import json

# redis 서버 연결
redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)

SESSION_TTL = 3600  # 세션 유지 시간(초)
MAX_RECENT_TURNS = 6  # "최근 대화"로 원문 그대로 보관할 메시지 개수 (user+assistant 합쳐서 6개 = 3턴)


## ======================= 세션 조회 =======================
async def get_session(session_id: str) -> dict:
    # Redis에서 이 세션ID의 대화 기록을 가져옴 (키 이름 앞에 "chat_session:" 붙여서 구분)
    raw = await redis_client.get(f"chat_session:{session_id}")
    if raw:
        return json.loads(raw)  # 저장할 때 JSON 문자열로 넣었으니 다시 파이썬 dict로 변환
    # 처음 대화하는 세션이면 빈 상태로 시작
    return {"summary": "", "recent_turns": []}


## ======================= 세션 저장 =======================
async def save_session(session_id: str, session_data: dict):
    # dict를 JSON 문자열로 바꿔서 Redis에 저장, ex=SESSION_TTL로 만료시간도 같이 지정
    await redis_client.set(
        f"chat_session:{session_id}",
        json.dumps(session_data, ensure_ascii=False),  # ensure_ascii=False: 한글이 유니코드 이스케이프(\uXXXX) 안 되고 그대로 저장됨
        ex=SESSION_TTL
    )


## ======================= 대화 한 턴 추가 + 오래된 대화 압축 =======================
async def append_turn(session_id: str, user_msg: str, assistant_msg: str, summarize_fn):
    # summarize_fn: 요약을 수행할 함수를 외부(chat_service.py)에서 주입받음
    # (redis_session.py가 OpenAI 호출 코드를 직접 알 필요 없게 분리한 것)

    session = await get_session(session_id)  # 지금까지의 대화 상태 불러오기

    # 이번 턴(사용자 질문 + 챗봇 답변)을 "최근 대화" 리스트에 추가
    session["recent_turns"].append({"role": "user", "content": user_msg})
    session["recent_turns"].append({"role": "assistant", "content": assistant_msg})

    # 최근 대화가 너무 길어지면(임계치 초과) 오래된 부분을 요약으로 압축
    if len(session["recent_turns"]) > MAX_RECENT_TURNS:
        old = session["recent_turns"][:-MAX_RECENT_TURNS]  # 임계치 넘는 만큼의 "오래된" 대화만 추출
        session["summary"] = await summarize_fn(old, session["summary"])  # 기존 요약 + 오래된 대화 -> 새 요약 생성
        session["recent_turns"] = session["recent_turns"][-MAX_RECENT_TURNS:]  # 최근 것만 남기고 나머지는 버림

    await save_session(session_id, session)  # 갱신된 상태 다시 Redis에 저장