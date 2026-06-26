import os
import requests
import time

from dotenv import load_dotenv

from service_example import getKisToken
from database import getStockMstList, insert_stock_minute2_bulk

load_dotenv(dotenv_path="../../dataset/config/.env")

## token 발행
# KIS_TOKEN = getKisToken()

KIS_APP_KEY = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET")
KIS_URL = os.getenv("KIS_URL")
KIS_USER_ID = os.getenv("KIS_USER_ID")


def retryGet(url, headers, params, maxRetry=7, sleepSec=0.5):
    """
    GET 요청 실패 시 최대 maxRetry회 재시도 (선형 백오프: 2s, 4s, 6s ...).
    - ConnectionError / Timeout / 429 → 재시도
    - 그 외 HTTPError (4xx/5xx 등)    → 즉시 raise
    """
    lastErr = None
    secWeight = 0.2

    for attempt in range(maxRetry):

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)

            if resp.status_code in [429, 500, 503]: # 429 외에도 500(거래내역없음) 등의 에러 발생으로 코드 추가
                wait = sleepSec * (attempt + secWeight)

                print(f"  [retry {attempt+1}/{maxRetry}] /code {resp.status_code}/ Rate limit, {wait}s 대기")

                time.sleep(wait)
                lastErr = requests.exceptions.HTTPError("429 Too Many Requests")

                continue
            resp.raise_for_status()

            return resp
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ChunkedEncodingError) as e:

            lastErr = e

            if attempt < maxRetry - 1:
                wait = sleepSec * (attempt + secWeight)

                print(f"  [retry {attempt + secWeight}/{maxRetry}] {type(e).__name__}, {wait}s 대기")

                time.sleep(wait)
        except requests.exceptions.HTTPError:
            raise
        except Exception as e:
            raise
    raise lastErr or RuntimeError("retryGet 최대 재시도 초과")



def inquire_time_itemchartprice(type: str, FID_INPUT_ISCD: str, FID_INPUT_HOUR_1: str, KIS_TOKEN:str):
    url = f"{KIS_URL}/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {KIS_TOKEN}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "FHKST03010200",
        "custtype": "P"
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": FID_INPUT_ISCD,
        "FID_INPUT_HOUR_1": FID_INPUT_HOUR_1,
        "FID_PW_DATA_INCU_YN": "Y",
        "FID_ETC_CLS_CODE": "",
    }

    # requests.get 대신 retryGet 사용 (네트워크 오류 자동 재시도)
    response = retryGet(url, headers, params, maxRetry=5, sleepSec=0.5)

    data = response.json()

    if data.get("rt_cd") == "0":

        return data.get("output1") if type == "output1" else data.get("output2")
    else:
        raise Exception(f"주식당일분봉조회 호출 실패: {response.text}")
