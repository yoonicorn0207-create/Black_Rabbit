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

def get_stock_list():
    """DB에서 ACTIVE 상태인 종목 리스트 가져오기"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT ticker FROM HC_stock_master WHERE status = 'ACTIVE'"
            cursor.execute(sql)
            return [row['ticker'] for row in cursor.fetchall()]
    finally:
        conn.close()

def save_to_mysql(table_name, data_dict):
    """데이터 저장 (UPSERT)"""
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

def fetch_and_store(stock_code, table1, table2, period_code):
    """일봉/주봉/월봉 구분 수집 함수"""
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
            "FID_PERIOD_DIV_CODE": period_code, # 'D', 'W', 또는 'M'
            "FID_ORG_ADJ_PRC": "0"
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
            if output1: save_to_mysql(table1, clean_data(output1))
            for row in data.get('output2', []):
                save_to_mysql(table2, clean_data(row))

        current_end = current_start - timedelta(days=1)
        time.sleep(0.5)
    print(f"[{stock_code}] {period_code} 유형 데이터 수집 완료.")

if __name__ == "__main__":
    stock_codes = get_stock_list()
    for code in stock_codes:
        print(f"\n>>> [{code}] 주봉 및 월봉 추가 수집 시작")

        # 주봉 수집
        fetch_and_store(code, "HC_stock_weekly1", "HC_stock_weekly2", "W")

        # 월봉 수집
        fetch_and_store(code, "HC_stock_monthly1", "HC_stock_monthly2", "M")