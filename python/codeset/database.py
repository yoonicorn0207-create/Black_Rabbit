import pymysql
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from service.stocks_info.kis_kospi_code_mst import get_market_master_dataframe
from service.stocks_info.kis_kosdaq_code_mst import get_kosdaq_master_dataframe

load_dotenv(dotenv_path="..\dataset\config\.env")

def get_db_connection():
    """ MySQL 연결 설정 """
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "ai_analyzer"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def createHcStockMasterTable():
    """
    매일 모든 api 호출 직전 현재 상장중인 종목들의 리스트를 호출하여
    종목 마스터테이블을 업데이트 한다.
    이때 상장 폐지 종목 등을 구분하기 위해 status 컬럼이 추가됨
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
            CREATE TABLE IF NOT EXISTS HC_stock_master (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL UNIQUE,          -- 종목코드 (예: 005930)
                stock_name VARCHAR(100) NOT NULL,            -- 종목명 (예: 삼성전자)
                market_type VARCHAR(10) NOT NULL,            -- 시장구분 (KOSPI, KOSDAQ)
                status VARCHAR(20) DEFAULT 'ACTIVE',         -- 상태 ('ACTIVE': 상장, 'DELISTED': 상장폐지)
                listed_date DATE NULL,                        -- 주식 상장 일자
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- 최종 확인일
            );
            """
            cursor.execute(sql)

            connection.commit()
    except Exception as e:
        print(f"종목 마스터테이블 생성 중 에러 발생{e}")
    finally:
        connection.close()


def updateHcStockMasterPipeline():
    """
    한투 마스터 파일을 읽어와 순수 보통주만 필터링한 후,
    HC_stock_master 테이블에 Upsert하고 상장폐지 종목을 추적하는 완벽한 ETL 파이프라인 함수
    """
    print("========= 종목 마스터 동기화 시작 =========")

    # 1. 코스피 / 코스닥 마스터 데이터프레임 가져오기
    try:
        df_kospi = get_market_master_dataframe(market="kospi", verbose=True)
        df_kosdaq = get_market_master_dataframe(market="kosdaq", verbose=True)
    except Exception as e:
        print(f"한투 마스터 파일 다운로드 및 파싱 실패: {e}")
        return

    # 2. [수정 및 고도화] 한국투자증권 코드를 이용해 순수 보통주(기업 주식)만 먼저 필터링
    # 코스피: 그룹코드가 'ST'(주식)인 것만 남김 (ETF, ETN, 리츠 등 완벽 제거)
    if '그룹코드' in df_kospi.columns:
        df_kospi = df_kospi[df_kospi['그룹코드'] == 'ST']

    # 코스닥: 증권그룹구분코드가 주식 관련('ST': 벤처, 'UU': 일반, 'FS': 외국주식)인 것만 남김
    if '증권그룹구분코드' in df_kosdaq.columns:
        df_kosdaq = df_kosdaq[df_kosdaq['증권그룹구분코드'].isin(['ST', 'UU', 'FS'])]

    # 3. DB 스키마에 맞게 컬럼명 및 데이터 정제
    # 코스피 정제
    df_kospi = df_kospi[['단축코드', '한글명', '상장일자']].rename(
        columns={'단축코드': 'ticker', '한글명': 'stock_name', '상장일자': 'listed_date'}
    )
    df_kospi['market_type'] = 'KOSPI'

    # 코스닥 정제
    df_kosdaq = df_kosdaq[['단축코드', '한글종목명', '주식 상장 일자']].rename(
        columns={'단축코드': 'ticker', '한글종목명': 'stock_name', '주식 상장 일자': 'listed_date'}
    )
    df_kosdaq['market_type'] = 'KOSDAQ'

    # 두 시장 데이터 하나로 병합
    today_stocks = pd.concat([df_kospi, df_kosdaq], ignore_index=True)

    # 결측치 처리 및 날짜 포맷팅 (YYYY-MM-DD)
    today_stocks['listed_date'] = pd.to_datetime(today_stocks['listed_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    # 종목명이 비어있는 데이터 방어 처리
    today_stocks = today_stocks.dropna(subset=['ticker', 'stock_name'])

    today_date = datetime.now().strftime('%Y-%m-%d')

    # 4. DB 연결 및 데이터 적재 (Upsert)
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            print(f"총 {len(today_stocks)}건의 순수 주식 종목 데이터를 DB에 반영 중...")

            # 대량 데이터를 빠르게 넣기 위해 executemany 구조 사용
            upsert_sql = """
                         INSERT INTO HC_stock_master (ticker, stock_name, market_type, status, listed_date, updated_at)
                         VALUES (%s, %s, %s, 'ACTIVE', %s, NOW()) ON DUPLICATE KEY \
                         UPDATE \
                             stock_name = \
                         VALUES (stock_name), status = 'ACTIVE', updated_at = NOW(); \
                         """

            # 튜플 리스트로 변환하여 한 번에 실행
            data_tuples = [
                (row['ticker'], row['stock_name'], row['market_type'], row['listed_date'])
                for _, row in today_stocks.iterrows()
            ]
            cursor.executemany(upsert_sql, data_tuples)

            # 5. 상장 폐지(Delisted) 검사 및 반영
            print("상장 폐지 종목 검사 중...")
            delist_sql = """
                         UPDATE HC_stock_master
                         SET status = 'DELISTED'
                         WHERE status = 'ACTIVE' \
                           AND DATE (updated_at) \
                             < %s; \
                         """
            cursor.execute(delist_sql, (today_date,))

        connection.commit()
        print(f"[{today_date}] 종목 마스터 테이블(HC_stock_master) 적재 성공!")

    except Exception as e:
        connection.rollback()
        print(f"DB 적재 중 에러 발생: {e}")
    finally:
        connection.close()

