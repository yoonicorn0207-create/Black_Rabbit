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

    # 0. 실행 전 상태 스냅샷
    before_active_count = len(getStockMstList())
    print(f"[동기화 전] ACTIVE 종목 수: {before_active_count}건")

    # 1. 코스피 / 코스닥 마스터 데이터프레임 가져오기
    try:
        df_kospi = get_market_master_dataframe(market="kospi", verbose=True)
        df_kosdaq = get_market_master_dataframe(market="kosdaq", verbose=True)
    except Exception as e:
        print(f"한투 마스터 파일 다운로드 및 파싱 실패: {e}")
        return

    # 2. [수정 및 고도화] 한국투자증권 코드를 이용해 순수 보통주(기업 주식)만 먼저 필터링
    if '그룹코드' in df_kospi.columns:
        df_kospi = df_kospi[df_kospi['그룹코드'] == 'ST']

    if '증권그룹구분코드' in df_kosdaq.columns:
        df_kosdaq = df_kosdaq[df_kosdaq['증권그룹구분코드'].isin(['ST', 'UU', 'FS'])]

    print(f"[수집] 코스피 {len(df_kospi)}건 / 코스닥 {len(df_kosdaq)}건 (필터링 후)")

    # 3. DB 스키마에 맞게 컬럼명 및 데이터 정제
    df_kospi = df_kospi[['단축코드', '한글명', '상장일자']].rename(
        columns={'단축코드': 'ticker', '한글명': 'stock_name', '상장일자': 'listed_date'}
    )
    df_kospi['market_type'] = 'KOSPI'

    df_kosdaq = df_kosdaq[['단축코드', '한글종목명', '주식 상장 일자']].rename(
        columns={'단축코드': 'ticker', '한글종목명': 'stock_name', '주식 상장 일자': 'listed_date'}
    )
    df_kosdaq['market_type'] = 'KOSDAQ'

    today_stocks = pd.concat([df_kospi, df_kosdaq], ignore_index=True)

    today_stocks['listed_date'] = pd.to_datetime(today_stocks['listed_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    today_stocks = today_stocks.dropna(subset=['ticker', 'stock_name'])

    today_date = datetime.now().strftime('%Y-%m-%d')
    incoming_count = len(today_stocks)
    print(f"[정제 후] Upsert 대상: {incoming_count}건")

    # 4. DB 연결 및 데이터 적재 (Upsert)
    try:
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

        # 6. 실행 후 상태 스냅샷 + 변화량 요약
        after_active_count = len(getStockMstList())
        delta = after_active_count - before_active_count

        print(f"\n========= 종목 마스터 동기화 완료 =========")
        print(f"[동기화 전] ACTIVE {before_active_count}건")
        print(f"[동기화 후] ACTIVE {after_active_count}건")
        print(f"[변화량] {'+' if delta >= 0 else ''}{delta}건 (신규상장 유입분 - 상장폐지 처리분)")

    except Exception as e:
        print(f"{e}")



if __name__ == "__main__":
    setStockMstList()