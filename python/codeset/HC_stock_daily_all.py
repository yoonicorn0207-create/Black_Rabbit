import os
import requests
import json
import pymysql
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 1. 환경 변수 및 DB 설정
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
dotenv_path = os.path.abspath(os.path.join(current_dir, "..", "dataset", "config", ".env"))
load_dotenv(dotenv_path=dotenv_path, override=True)

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"),
        port=3306, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
    )

def getKisToken():
    url = f"{os.getenv('KIS_URL')}/oauth2/tokenP"
    body = {"grant_type": "client_credentials", "appkey": os.getenv("KIS_APP_KEY"), "appsecret": os.getenv("KIS_APP_SECRET")}
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

def get_last_collected_dates():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT stck_shrn_iscd, MAX(stck_bsop_date) as last_date FROM HC_stock_daily2 GROUP BY stck_shrn_iscd")
            return {row['stck_shrn_iscd']: row['last_date'] for row in cursor.fetchall()}
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

def fetch_and_store(stock_code, start_date_obj):
    token = getKisToken()
    headers = {
        "authorization": f"Bearer {token}", "appkey": os.getenv("KIS_APP_KEY"),
        "appsecret": os.getenv("KIS_APP_SECRET"), "tr_id": "FHKST03010100",
        "content-type": "application/json"
    }

    end_date = datetime.now()
    current_end = end_date

    # 목표 시작일 설정
    while current_end >= start_date_obj:
        current_start = current_end - timedelta(days=99)
        if current_start < start_date_obj: current_start = start_date_obj

        params = {
            "FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": current_start.strftime("%Y%m%d"),
            "FID_INPUT_DATE_2": current_end.strftime("%Y%m%d"),
            "FID_PERIOD_DIV_CODE": "D", "FID_ORG_ADJ_PRC": "0"
        }

        response = requests.get(f"{os.getenv('KIS_URL')}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
                                headers=headers, params=params)
        data = response.json()

        if data.get("rt_cd") == "0":
            for row in data.get('output2', []):
                row['stck_shrn_iscd'] = stock_code
                save_to_mysql("HC_stock_daily2", row)

        current_end = current_start - timedelta(days=1)
        time.sleep(0.5)

if __name__ == "__main__":
    all_codes = get_stock_list()
    last_dates = get_last_collected_dates()

    print(f"전체 대상 종목: {len(all_codes)}개 확인 완료.")

    for i, code in enumerate(all_codes):
        last_date_str = last_dates.get(code)

        if last_date_str:
            # 기존 종목: 마지막 날짜 다음 날부터 (최대 2년 전까지만 제한 가능)
            start_date = datetime.strptime(str(last_date_str), "%Y%m%d") + timedelta(days=1)
            mode = "증분 업데이트"
        else:
            # 신규 종목: 2년 전부터
            start_date = datetime.now() - timedelta(days=730)
            mode = "초기 전체 수집"

        if start_date <= datetime.now():
            print(f"[{i+1}/{len(all_codes)}] {code} [{mode}] 시작 (범위: {start_date.strftime('%Y-%m-%d')} ~ 현재)")
            try:
                fetch_and_store(code, start_date)
            except Exception as e:
                print(f"!!! [{code}] 에러 발생: {e}")
        else:
            print(f"[{i+1}/{len(all_codes)}] {code} - 최신 데이터 보유 중")

        time.sleep(1.0) # API 과부하 방지