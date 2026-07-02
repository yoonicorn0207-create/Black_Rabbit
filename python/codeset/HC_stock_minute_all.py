import os
import sys
from collections import deque
from datetime import datetime
import requests
import time

from common_api import getKisToken
from database import get_db_connection, patchSingleRow, patchAllRows, queryRows
from HC_stock_master import getStockMstList
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
dotenv_path = os.path.abspath(os.path.join(current_dir, "..", "dataset", "config", ".env"))
load_dotenv(dotenv_path=dotenv_path, override=True)

KIS_APP_KEY = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET")
KIS_URL = os.getenv("KIS_URL")
KIS_TOKEN = getKisToken()


## =========== 요청 시간을 이용하여 데이터 가져올 시간 계산 함수 =================
def getTargetTime():
    """
    크론탭 실행 시간을 기준으로 30분봉 수집이 완료된 시간 return
    10:34 호출 시 103000 출력
    """
    now = datetime.now()

    minute = 30 if now.minute >= 30 else 0

    target = now.replace(
        minute=minute,
        second=0,
        microsecond=0
    )

    return target.strftime("%H%M%S")


## =========== 요청 실패 시 재시도 함수 =================
def retryGet(url, headers, params, maxRetry=5, sleepSec=0.5):
    """
    GET 요청 실패 시 최대 maxRetry회 재시도 (선형 백오프: 2s, 4s, 6s ...).
    - ConnectionError / Timeout / 429 500 503 → 재시도
    - 그 외 HTTPError (4xx/5xx 등)    → 즉시 raise
    """
    lastErr = None
    secWeight = 0.2

    for attempt in range(maxRetry):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)

            if resp.status_code in [429, 500, 503]:  # 429 외에도 500(거래내역없음) 등의 에러 발생으로 코드 추가
                wait = sleepSec * (attempt + secWeight)

                print(f"  [retry {attempt + 1}/{maxRetry}] /code {resp.status_code}/ Rate limit, {wait}s 대기")

                time.sleep(wait)
                lastErr = requests.exceptions.HTTPError(f"{resp.status_code}")

                continue

            resp.raise_for_status()
            return resp

        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ChunkedEncodingError) as e:
            lastErr = e
            if attempt < maxRetry - 1:
                wait = sleepSec * (attempt + 1)
                print(f"  [retry {attempt+1}/{maxRetry}] {type(e).__name__}, {wait}s 대기")
                time.sleep(wait)

        except requests.exceptions.HTTPError:
            raise

        except Exception as e:
            raise

    raise lastErr or RuntimeError("retryGet 최대 재시도 초과")


## =========== api 1분에 18개 초과 호출 방지 =================
class RateLimiter:
    """
    30분 내에 api 호출 완료를 위한 슬라이딩 윈도우 레이트리미터
    무조건 1.2초를 쉬는 기존 코드와 달리 필요시에만 기다리기에 속도상 유리함
    ex)
    0.00초: 호출 → timestamps = [0.00]
    0.06초: 호출 → timestamps = [0.00, 0.06]
    ...
    0.94초: 18번째 호출 → timestamps = [0.00, 0.06, ..., 0.94]  ← 18개 꽉 참
    0.95초: 19번째 호출 시도
            → 가장 오래된 0.00초 기준으로 1.0 - 0.95 = 0.05초 대기
            → 1.00초에 호출, timestamps에서 0.00 제거 후 1.00 추가
    """
    def __init__(self, calls_per_sec=18):
        self.calls_per_sec = calls_per_sec
        self.timestamps = deque() # 최근 호출 시각 저장

    def wait(self):
        now = time.time()
        # 1초보다 오래된 기록 제거
        while self.timestamps and now - self.timestamps[0] >= 1.0:
            self.timestamps.popleft()

        # 1초 안에 18건 이상 쌓였을 경우 대기
        if len(self.timestamps) >= self.calls_per_sec:
            sleep_time = 1.0 - (now - self.timestamps[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.timestamps.append(time.time())


## =========== 분봉 호출 api =================
def inquire_time_itemchartprice( FID_INPUT_ISCD: str, FID_INPUT_HOUR_1: str):
    """
    :param FID_INPUT_ISCD: 종목명
    :param FID_INPUT_HOUR_1: 시간
    :return:
    """
    try:
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
        response = retryGet(url, headers, params)

        data = response.json()
        if data.get("rt_cd") == "0":
            return data
            # return data.get("output1") if type == "output1" else data.get("output2")
        else:
            raise Exception(f"주식당일분봉조회 호출 실패: {response.text}")

    except Exception as e:
        raise Exception(f"주식당일분봉조회 호출 실패: {e}")



## =========== DB insert 로직1 =================
def insert_stock_minute1(ticker, out1_data):
    """ output1 (당일 요약) 데이터를 minute1 테이블에 적재/업데이트 """
    try:
        if not out1_data:
            return

        sql = """
              INSERT INTO HC_stock_minute1 (ticker, 
                                            stck_bsop_date, 
                                            stck_prpr, 
                                            prdy_vrss, 
                                            prdy_vrss_sign, 
                                            prdy_ctrt, 
                                            stck_prdy_clpr, 
                                            acml_vol, 
                                            acml_tr_pbmn, 
                                            hts_kor_isnm)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
              ON DUPLICATE KEY UPDATE 
                  stck_prpr = VALUES(stck_prpr), 
                  prdy_vrss = VALUES(prdy_vrss), 
                  prdy_vrss_sign = VALUES(prdy_vrss_sign), 
                  prdy_ctrt = VALUES(prdy_ctrt), 
                  stck_prdy_clpr = VALUES(stck_prdy_clpr), 
                  acml_vol = VALUES(acml_vol), 
                  acml_tr_pbmn = VALUES(acml_tr_pbmn), 
                  hts_kor_isnm = VALUES(hts_kor_isnm);
              """

        params = (
            ticker,
            out1_data.get('stck_bsop_date'),
            out1_data.get('stck_prpr', 0),
            out1_data.get('prdy_vrss', 0),
            out1_data.get('prdy_vrss_sign', '0'),  # 핵심: 키가 없으면 '0' 반환
            out1_data.get('prdy_ctrt', 0.0),
            out1_data.get('stck_prdy_clpr', 0),
            out1_data.get('acml_vol', 0),
            out1_data.get('acml_tr_pbmn', 0),
            out1_data.get('hts_kor_isnm', '알수없음')
        )

        patchSingleRow(sql, "DB 적재 중 에러 발생", params)

    except Exception as e:
        print(f"DB 적재 중 에러 발생: {e}")


## =========== DB insert 로직2 =================
def insert_stock_minute2_bulk(minute2_tuples):
    """ 한 종목의 수집된 하루치 분봉 리스트(튜플 배열)를 묶어서 한번에 쏘기(Bulk Insert) """
    try:
        if not minute2_tuples:
            return
        sql = """
            INSERT INTO HC_stock_minute2 (
                ticker, 
                stck_bsop_date, 
                stck_cntg_hour, 
                stck_oprc, 
                stck_hgpr, 
                stck_lwpr, 
                stck_prpr, 
                cntg_vol, 
                acml_tr_pbmn
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                stck_oprc = VALUES(stck_oprc), 
                stck_hgpr = VALUES(stck_hgpr),
                stck_lwpr = VALUES(stck_lwpr), 
                stck_prpr = VALUES(stck_prpr),
                cntg_vol = VALUES(cntg_vol), 
                acml_tr_pbmn = VALUES(acml_tr_pbmn);
        """
        patchAllRows(sql, minute2_tuples, "DB 적재 중 에러 발생")

    except Exception as e:
        print(f"DB 적재 중 에러 발생: {e}")


## =========== 반복문 처리 =================
TIMEOUT_MINUTES = 25  # 30분 크론 기준, 25분 안에 강제 종료

def get_itemchartprice_data():
    """
    크론으로 작동되는 코드
    """
    ## api 호출 시간 TIMEOUT_MINUTES 이상으로 넘어가지 못하게끔
    start_time = time.time()
    limiter = RateLimiter(calls_per_sec=18) ## api 호출- 1초에 18번 초과되지 못하게 처리

    try:

        tickersList = getStockMstList() ## 오늘 상장한 종목 리스트 가져오기
        target_time = getTargetTime() ## 호출할 분봉 데이터 시간 계산
        total_len = len(tickersList) ## 상장 종목 갯수

        # targetTimes = [
        #   "153000", "150000", "143000", "140000",
        #   "133000", "130000", "123000", "120000",
        #   "113000", "110000", "103000", "100000", "093000"]

        print(f"📌 수집 시작 | 기준시각: {target_time} | 종목 수: {total_len}")

        ## 시간 단위로 호출되는 api이므로 종목을 기준으로 반복문 진행
        for idx, ticker in enumerate(tickersList, 1):

            ## TIMEOUT_MINUTES 로직
            elapsed = (time.time() - start_time) / 60
            if elapsed >= TIMEOUT_MINUTES:
                print(f"⏰ {TIMEOUT_MINUTES}분 초과로 강제 종료 (진행: {idx-1}/{total_len})")
                break

            arr = []
            arr_meta = {}
            success = False
            retry_count = 0

            ## 최대 3번까지 시도하고 실패 시 다음 종목으로 이동
            while not success and retry_count < 3:
                try:
                    limiter.wait()  # 고정 sleep 대신 레이트리미터
                    res = inquire_time_itemchartprice(ticker, target_time) ## 분봉 호출 api

                    success = True
                except Exception as api_e:
                    error_msg = str(api_e)

                    if "EGW00201" in error_msg or "초당 거래건수" in error_msg:
                        retry_count += 1
                        print(f"   ⚠️ [{ticker}] 초당 제한. 3초 대기 후 재시도... ({retry_count}/3)")
                        time.sleep(3)

                    else:
                        print(f"   ❌ [{ticker}] 에러: {api_e}")
                        break

            if success and res:
                res_list = res.get('output2', [])
                b_date = ''

                if success and res:

                    for row in res_list:
                        b_date = f"{row['stck_bsop_date'][:4]}-{row['stck_bsop_date'][4:6]}-{row['stck_bsop_date'][6:]}"
                        c_hour = f"{row['stck_cntg_hour'][:2]}:{row['stck_cntg_hour'][2:4]}:{row['stck_cntg_hour'][4:]}"

                        arr.append((
                            ticker, b_date, c_hour, row['stck_oprc'],
                            row['stck_hgpr'], row['stck_lwpr'], row['stck_prpr'],
                            row['cntg_vol'], row['acml_tr_pbmn']
                        ))

                    if target_time == '153000':
                        out1 = res.get('output1', {})

                        # arr_meta에 적절한 값 넣기
                        arr_meta = {
                            'ticker': ticker,
                            "stck_bsop_date": b_date,
                            'stck_prpr': out1.get('stck_prpr', 0),
                            'prdy_vrss': out1.get('prdy_vrss', 0),
                            'prdy_vrss_sign': out1.get('prdy_vrss_sign', '0'),
                            'prdy_ctrt': out1.get('prdy_ctrt', 0.0),
                            'stck_prdy_clpr': out1.get('stck_prdy_clpr', 0),
                            'acml_vol': out1.get('acml_vol', 0),
                            'acml_tr_pbmn': out1.get('acml_tr_pbmn', 0),
                            'hts_kor_isnm': out1.get('hts_kor_isnm', '알수없음')
                        }

            if arr:
                try:
                    if target_time == '153000':
                        insert_stock_minute1(ticker, arr_meta)

                    insert_stock_minute2_bulk(arr)

                    print(f"[{idx-1}/{total_len}] {target_time} 완료")
                except Exception as db_e:
                    print(f"   ❌ [{ticker}] DB 적재 실패: {db_e}")

        elapsed_total = (time.time() - start_time)
        print(f"✅ 수집 완료 | 소요시간: {elapsed_total:.1f}초")

    except Exception as e:
        print(f"🚨 치명적 에러: {e}")


if __name__ == "__main__":
    get_itemchartprice_data();