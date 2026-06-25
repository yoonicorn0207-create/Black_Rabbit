import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from decimal import Decimal

current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
dotenv_path = os.path.abspath(os.path.join(current_dir, "..", "dataset", "config", ".env"))

load_dotenv(dotenv_path=dotenv_path, override=True)

KIS_APP_KEY = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET")
KIS_URL = os.getenv("KIS_URL")
KIS_USER_ID = os.getenv("KIS_USER_ID")

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
