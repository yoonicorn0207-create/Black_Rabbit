import os
import json
import asyncio
import websockets
import requests
from dotenv import load_dotenv
from database import patchSingleRow

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '..', 'dataset', 'config', '.env')
load_dotenv(dotenv_path=env_path)

# 인증키 발급 함수
def get_approval(key, secret):
    url = os.getenv('KIS_URL')
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials", "appkey": key, "secretkey": secret}
    res = requests.post(f"{url}/oauth2/Approval", headers=headers, data=json.dumps(body))
    result = res.json()
    if "approval_key" not in result:
        raise Exception(f"인증 실패: {result}")
    return result["approval_key"]

async def connect():
    g_appkey = os.getenv('KIS_APP_KEY')
    g_appsecret = os.getenv('KIS_APP_SECRET')
    url = os.getenv('KIS_WS_URL')

    # 무한 루프를 통해 연결이 끊겨도 재접속 시도
    while True:
        try:
            g_approval_key = get_approval(g_appkey, g_appsecret)

            async with websockets.connect(url, ping_interval=None) as websocket:
                # KOSPI(0001), KOSDAQ(1001) 구독 요청
                for tr_key in ['0001', '1001']:
                    subscribe_data = {
                        "header": {"approval_key": g_approval_key, "custtype": "P", "tr_type": "1", "content-type": "utf-8"},
                        "body": {"input": {"tr_id": "H0SICA00", "tr_key": tr_key}}
                    }
                    await websocket.send(json.dumps(subscribe_data))
                    await asyncio.sleep(0.1)

                print("지수 데이터 수신 대기 중...")
                while True:
                    data = await websocket.recv()

                    # 데이터 수신 및 처리
                    if data and data[0] == '0':
                        recvstr = data.split('|')
                        if len(recvstr) > 3 and recvstr[1] == "H0SICA00":
                            tr_key, current_val = recvstr[2], recvstr[3]

                            # DB 업데이트 쿼리
                            sql = """INSERT INTO HC_realtime_indices (tr_key, current_val)
                                     VALUES (%s, %s) ON DUPLICATE KEY UPDATE current_val = %s"""
                            patchSingleRow(sql, "지수 업데이트 실패", (tr_key, current_val, current_val))
                            print(f"[{'KOSPI' if tr_key == '0001' else 'KOSDAQ'}] 업데이트 완료: {current_val}")

                    elif "PINGPONG" in data:
                        print("PINGPONG 수신")

        except Exception as e:
            print(f"연결 오류 또는 서버 종료: {e}. 5초 후 재접속합니다.")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(connect())