import asyncio
import websockets
import json
import orjson
import os
from dotenv import load_dotenv

# 환경변수 로드 (위에서 성공한 경로 설정 방식을 그대로 사용하세요)
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.abspath(os.path.join(current_dir, "..", "dataset", "config", ".env"))
load_dotenv(dotenv_path=env_path)

# 접속 정보 가져오기
APP_KEY = os.getenv("KIS_APP_KEY")
APP_SECRET = os.getenv("KIS_APP_SECRET")
WS_URL = os.getenv("KIS_WS_URL")  # .env에 추가하셨던 그 주소입니다.


async def connect_kis_websocket():
    print(f"웹소켓 연결 시도 중: {WS_URL}")

    async with websockets.connect(WS_URL) as ws:
        print("연결 성공!")

        # 여기서 서버로 보낼 구독 메시지(JSON)를 작성해야 합니다.
        # 예: KOSPI 지수 구독
        subscribe_data = {
            "header": {
                "approval_key": "발급받은_접속키를_여기에",
                "custtype": "P",
                "tr_type": "1",
                "content-type": "utf-8"
            },
            "body": {
                "input": {
                    "tr_id": "H0STCNT0",  # KOSPI 지수 TR ID
                    "tr_key": "0001"
                }
            }
        }

        await ws.send(json.dumps(subscribe_data))

        # 서버로부터 데이터가 들어오는지 무한 루프 대기
        while True:
            recv_data = await ws.recv()
            data = orjson.loads(recv_data)
            print("수신 데이터:", data)


if __name__ == "__main__":
    asyncio.run(connect_kis_websocket())
