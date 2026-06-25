import os
import requests
import json
import pymysql
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 1. 설정: .env 파일 로드
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
dotenv_path = os.path.abspath(os.path.join(current_dir, "..", "dataset", "config", ".env"))
load_dotenv(dotenv_path=dotenv_path, override=True)

# 환경 변수 가져오기
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

# [추가됨] DB에서 종목 리스트를 가져오는 함수
def get_stock_list():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # [수정] status가 'ACTIVE'인 종목만 가져오도록 SQL 변경
            sql = "SELECT ticker FROM HC_stock_master WHERE status = 'ACTIVE'"
            cursor.execute(sql)
            return [row['ticker'] for row in cursor.fetchall()]
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
            sql = f"INSERT INTO {table_name} ({cols}) VALUES ({', '.join(['%s']*len(keys))}) ON DUPLICATE KEY UPDATE {update_stmt}"
            cursor.execute(sql, vals)
        conn.commit()
    finally:
        conn.close()

def print_preview(data):
    print("\n" + "="*70)
    output1 = data.get('output1', {})
    print(f">>> [Output1] 기업 정보 요약:")
    for key, value in output1.items():
        print(f"  {key:<20} : {value}")

    output2_list = data.get('output2', [])
    print(f"\n>>> [Output2] 시세 데이터 (이번 구간 총 {len(output2_list)}건):")
    if output2_list:
        print(">>> 상세 데이터 (상위 5건):")
        for i, row in enumerate(output2_list[:5]):
            print(f"  [{i+1}] 날짜: {row.get('stck_bsop_date')} | 종가: {row.get('stck_clpr')} | 거래량: {row.get('acml_vol')}")
    print("="*70 + "\n")

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

        print_preview(data)

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
    # DB의 HC_stock_info 테이블에서 리스트를 가져와 자동으로 수집
    stock_codes = get_stock_list()
    for code in stock_codes:
        print(f"\n>>> [{code}] 종목 수집 시작")
        fetch_and_store_2years(code)