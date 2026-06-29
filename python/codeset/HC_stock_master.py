import pandas as pd
from datetime import datetime

from database import queryRows, patchAllRows, patchSingleRow
from kis_stock_code.kis_kospi_code_mst import get_market_master_dataframe


def getStockMstList():
    """
    종목 마스터 테이블에서 현재 상장되어 있는 종목 코드 가져오기
    """
    try:
        sql = """
        select ticker
        from HC_stock_master
        where 1=1
            and status = "ACTIVE"
        """
        rows = queryRows(sql, "테이블 조회 중 에러 발생" )

        ticker_list = [row['ticker'] for row in rows]

        return ticker_list
    except Exception as e:
        print(f"{e}")
        return []


def setStockMstList():
    """
    한투 마스터 파일을 읽어와 순수 보통주만 필터링한 후,
    HC_stock_master 테이블에 Upsert하고 상장폐지 종목 추적 ETL 파이프라인 함수
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
    try:
        # 대량 데이터를 빠르게 넣기 위해 executemany 구조 사용
        upsert_sql = """
            INSERT INTO HC_stock_master (
                ticker, 
                stock_name, 
                market_type, 
                status, 
                listed_date, 
                updated_at
            )
            VALUES (%s, %s, %s, 'ACTIVE', %s, NOW())
            ON DUPLICATE KEY UPDATE
                stock_name = VALUES(stock_name),
                status = 'ACTIVE',
                updated_at = NOW();
        """

        # 튜플 리스트로 변환하여 한 번에 실행
        data_tuples = [
            (row['ticker'], row['stock_name'], row['market_type'], row['listed_date'])
            for _, row in today_stocks.iterrows()
        ]

        patchAllRows(upsert_sql, data_tuples, "DB 적재 중 에러 발생")

        # 5. 상장 폐지(Delisted) 검사 및 반영
        print("상장 폐지 종목 검사 중...")
        delist_sql = """
            UPDATE HC_stock_master
            SET status = 'DELISTED'
            WHERE status = 'ACTIVE' AND DATE(updated_at) < %s;
        """
        patchSingleRow(delist_sql, "DB 적재 중 에러 발생", (today_date,))

    except Exception as e:
        print(f"{e}")



if __name__ == "__main__":
    setStockMstList()