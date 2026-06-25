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

def getStockMstList():
    """
    종목 마스터 테이블에서 현재 상장되어 있는 종목 코드 가져오기
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
            select ticker
            from HC_stock_master
            where 1=1
                and status = "ACTIVE"
            """
            cursor.execute(sql)

            rows = cursor.fetchall()
            ticker_list = [row['ticker'] for row in rows]

            return ticker_list
    except Exception as e:
        print(f"테이블 생성 중 에러 발생{e}")
        return []
    finally:
        connection.close()


def createTalbe(sql):
    """
    테이블 생성 공통 함수
    :param sql:
    :return:
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)

        connection.commit()
    except Exception as e:
        print(f"테이블 생성 중 에러 발생{e}")
    finally:
        connection.close()


def initialize_all_tables():
    """ 프로젝트에 필요한 모든 테이블을 한 번에 초기화하는 함수 """
    print("========= 데이터베이스 테이블 초기화 시작 =========")

    # 생성할 테이블 쿼리들을 딕셔너리로 관리 (가독성 향상)
    tables_sql = {
        "HC_stock_master": """
                           CREATE TABLE IF NOT EXISTS HC_stock_master
                           (
                               id
                               INT
                               AUTO_INCREMENT
                               PRIMARY
                               KEY,
                               ticker
                               VARCHAR
                           (
                               10
                           ) NOT NULL UNIQUE,
                               stock_name VARCHAR
                           (
                               100
                           ) NOT NULL,
                               market_type VARCHAR
                           (
                               10
                           ) NOT NULL,
                               status VARCHAR
                           (
                               20
                           ) DEFAULT 'ACTIVE',
                               listed_date DATE NULL,
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                               ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                           """,

        "HC_stock_minute1": """
                            CREATE TABLE IF NOT EXISTS HC_stock_minute1
                            (
                                id
                                BIGINT
                                AUTO_INCREMENT
                                PRIMARY
                                KEY,
                                ticker
                                VARCHAR
                            (
                                10
                            ) NOT NULL COMMENT '종목코드 (예: 005930)',
                                stck_bsop_date DATE NOT NULL COMMENT '영업 일자 (YYYY-MM-DD)',
                                stck_prpr INT NOT NULL COMMENT '당일 최종 종가 (주식 현재가)',
                                prdy_vrss INT NOT NULL COMMENT '전일 대비 등락폭',
                                prdy_ctrt DECIMAL
                            (
                                5,
                                2
                            ) NOT NULL COMMENT '전일 대비 등락률',
                                acml_vol BIGINT NOT NULL COMMENT '당일 누적 거래량',
                                acml_tr_pbmn BIGINT NOT NULL COMMENT '당일 누적 거래대금',
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '시스템 데이터 적재 시간',
                                UNIQUE KEY uq_ticker_date
                            (
                                ticker,
                                stck_bsop_date
                            )
                                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='한국투자증권 output1 기준 당일 마감 일별 요약 테이블';
                            """,

        "HC_stock_minute2": """
                            CREATE TABLE IF NOT EXISTS HC_stock_minute2
                            (
                                id
                                BIGINT
                                AUTO_INCREMENT
                                PRIMARY
                                KEY,
                                ticker
                                VARCHAR
                            (
                                10
                            ) NOT NULL COMMENT '종목코드 (예: 005930)',
                                stck_bsop_date DATE NOT NULL COMMENT '영업 일자 (YYYY-MM-DD)',
                                stck_cntg_hour TIME NOT NULL COMMENT '주식 체결 시간 / 분봉 시간 (HH:MM:SS)',
                                stck_oprc INT NOT NULL COMMENT '주식 시가 (해당 분 시작 가격)',
                                stck_hgpr INT NOT NULL COMMENT '주식 고가 (해당 분 최고 가격)',
                                stck_lwpr INT NOT NULL COMMENT '주식 저가 (해당 분 최저 가격)',
                                stck_prpr INT NOT NULL COMMENT '주식 현재가 / 종가 (해당 분 마감 가격)',
                                cntg_vol BIGINT NOT NULL COMMENT '체결 거래량 (해당 1분 동안 터진 거래량)',
                                acml_tr_pbmn BIGINT NOT NULL COMMENT '누적 거래대금 (당일 장 시작부터 해당 분까지의 누적치)',
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '시스템 데이터 적재 시간',
                                UNIQUE KEY uq_ticker_date_time
                            (
                                ticker,
                                stck_bsop_date,
                                stck_cntg_hour
                            )
                                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='한국투자증권 output2 기준 1분 단위 분봉 적재 테이블';
                            """
    }

    # 텍스트 리스트(딕셔너리 키/값)를 돌면서 공통 함수 호출
    for table_name, sql_query in tables_sql.items():
        print(f"[{table_name}] 테이블 생성 확인 중...")
        createTalbe(sql_query)

    print("========= 모든 테이블 초기화 완료 =========")





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
