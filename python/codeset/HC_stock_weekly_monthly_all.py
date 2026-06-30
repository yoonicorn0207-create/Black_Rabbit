import os
import requests
import json
import pymysql
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 1. 설정
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

def get_stock_list():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ticker FROM HC_stock_master WHERE status = 'ACTIVE'")
            return [row['ticker'] for row in cursor.fetchall()]
    finally:
        conn.close()

def get_last_date(table_name, stock_code):
    """DB에서 해당 종목의 마지막 수집 날짜 조회"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = f"SELECT MAX(stck_bsop_date) as last_date FROM {table_name} WHERE stck_shrn_iscd = %s"
            cursor.execute(sql, (stock_code,))
            result = cursor.fetchone()
            return result['last_date'] if result and result['last_date'] else None
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

def fetch_and_store(stock_code, table1, table2, period_code):
    last_date_str = get_last_date(table2, stock_code)

    # 마지막 수집 날짜 다음 날부터 수집 시작
    if last_date_str:
        start_date = datetime.strptime(last_date_str, "%Y%m%d") + timedelta(days=1)
    else:
        start_date = datetime.now() - timedelta(days=730)

    end_date = datetime.now()
    if start_date > end_date:
        print(f"    - {period_code} 최신 상태입니다.")
        return

    token = getKisToken()
    headers = {"authorization": f"Bearer {token}", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET,
               "tr_id": "FHKST03010100", "content-type": "application/json"}

    current_end = end_date
    while current_end >= start_date:
        current_start = current_end - timedelta(days=99)
        if current_start < start_date: current_start = start_date

        params = {
            "FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": current_start.strftime("%Y%m%d"),
            "FID_INPUT_DATE_2": current_end.strftime("%Y%m%d"),
            "FID_PERIOD_DIV_CODE": period_code, "FID_ORG_ADJ_PRC": "0"
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
    print(f"    - {period_code} 수집 완료.")

if __name__ == "__main__":
    stock_codes = get_stock_list()
    total = len(stock_codes)

    for i, code in enumerate(stock_codes, 1):
        print(f"[{i}/{total}] [{code}] 업데이트 시작")
        fetch_and_store(code, "HC_stock_weekly1", "HC_stock_weekly2", "W")
        fetch_and_store(code, "HC_stock_monthly1", "HC_stock_monthly2", "M")
        time.sleep(0.5)