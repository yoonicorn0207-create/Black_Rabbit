import os
import requests
import json
from dotenv import load_dotenv

from database import patchSingleRow

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "../dataset/config/.env"), override=True)

KIS_APP_KEY = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET")
KIS_URL = os.getenv("KIS_URL")
KIS_USER_ID = os.getenv("KIS_USER_ID")



## =========== token 생성 api =================
def getKisToken():
  """
  1. api 호출에 필요한 token 생성
  """
  try:
    url=f"{KIS_URL}/oauth2/tokenP"
    headers = {
      "content-type": "application/json"
    }
    body = {
      "grant_type" : "client_credentials",
      "appkey" : KIS_APP_KEY,
      "appsecret" : KIS_APP_SECRET,
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))

    token = response.json().get("access_token")

    # 1. None이 아니고 2. 타입이 문자열이며 3. 공백을 제거해도 내용이 있는 경우
    if token and isinstance(token, str) and token.strip():
      return token
    else:
        raise Exception(f"토큰 발급 실패: {response.text}")
  except Exception as e:
     print(f"토큰 발급 api 호출 중 error 발생: {e}")
