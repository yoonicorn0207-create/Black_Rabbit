import os
import requests
import json
import pymysql
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 1. 환경 변수 설정
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
dotenv_path = os.path.abspath(os.path.join(current_dir, "..", "dataset", "config", ".env"))
load_dotenv(dotenv_path=dotenv_path, override=True)

KIS_APP_KEY = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET")
KIS_URL = os.getenv("KIS_URL")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def get_db_connection():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                           database=DB_NAME, port=3306, charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)


def getKisToken():
    url = f"{KIS_URL}/oauth2/tokenP"
    body = {"grant_type": "client_credentials", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET}
    response = requests.post(url, headers={"content-type": "application/json"}, data=json.dumps(body))
    return response.json().get("access_token")


# 전체 리스트 조회 함수
def get_stock_list():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT ticker FROM HC_stock_master WHERE status = 'ACTIVE'"
            cursor.execute(sql)
            return [row['ticker'] for row in cursor.fetchall()]
    finally:
        conn.close()


# [2026-06-26 추가] 이미 수집된 종목 확인 함수
def get_already_collected_tickers():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT DISTINCT stck_shrn_iscd FROM HC_stock_daily2"
            cursor.execute(sql)
            return [row['stck_shrn_iscd'] for row in cursor.fetchall()]
    finally:
        conn.close()


def save_to_mysql(table_name, data_dict):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            keys = list(data_dict.keys())
            cols = ", ".join([f"`{k}`" for k in keys])
            vals = [data_dict[k] for k in keys]
            update_stmt = ", ".join([f"`{k}`=VALUES(`{k}`)" for k in keys])
            sql = f"INSERT INTO {table_name} ({cols}) VALUES ({', '.join(['%s'] * len(keys))}) ON DUPLICATE KEY UPDATE {update_stmt}"
            cursor.execute(sql, vals)
        conn.commit()
    finally:
        conn.close()


def fetch_and_store_2years(stock_code):
    token = getKisToken()
    headers = {"authorization": f"Bearer {token}", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET,
               "tr_id": "FHKST03010100", "content-type": "application/json"}

    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    current_end = end_date

    while current_end > start_date:
        current_start = current_end - timedelta(days=99)
        if current_start < start_date: current_start = start_date

        params = {
            "FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": current_start.strftime("%Y%m%d"),
            "FID_INPUT_DATE_2": current_end.strftime("%Y%m%d"),
            "FID_PERIOD_DIV_CODE": "D", "FID_ORG_ADJ_PRC": "0"
        }

        response = requests.get(f"{KIS_URL}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
                                headers=headers, params=params)
        data = response.json()

        if data.get("rt_cd") == "0":
            def clean_data(d):
                keys_to_fix = [k for k in d.keys() if k.endswith(" name")]
                for k in keys_to_fix:
                    clean_key = k.replace(" name", "")
                    d[clean_key] = d.pop(k)
                d['stck_shrn_iscd'] = stock_code
                return d

            output1 = data.get('output1', {})
            if output1: save_to_mysql("HC_stock_daily1", clean_data(output1))
            for row in data.get('output2', []):
                save_to_mysql("HC_stock_daily2", clean_data(row))

        current_end = current_start - timedelta(days=1)
        time.sleep(0.5)

    print(f"[{stock_code}] 모든 데이터 수집 및 DB 저장 완료.")


if __name__ == "__main__":
    # 1. DB에서 전체 ACTIVE 종목 리스트 가져오기
    all_codes = get_stock_list()

    # 2. 이미 수집된 종목 리스트 가져오기 (2026-06-26 업데이트)
    collected_codes = get_already_collected_tickers()

    # 3. [핵심] 차집합 연산 (전체 - 이미 수집됨 = 남은 종목)
    codes_to_collect = [code for code in all_codes if code not in collected_codes]

    print(f"전체: {len(all_codes)}개 | 이미 수집됨: {len(collected_codes)}개 | 남은 종목: {len(codes_to_collect)}개")

    # 4. 남은 종목만 순차적으로 수집
    for code in codes_to_collect:
        try:
            print(f"\n>>> [{code}] 수집 시작")
            fetch_and_store_2years(code)
            time.sleep(1.0)
        except Exception as e:
            print(f"!!! [{code}] 에러 발생, 다음 종목으로 진행합니다: {e}")
            continue
