from database import patchSingleRow


## =========== 처음 실행 시 테이블 초기화  =================
def initialize_all_tables():
    """ 프로젝트에 필요한 모든 테이블을 한 번에 초기화하는 함수 """
    print("========= 데이터베이스 테이블 초기화 시작 =========")

    # 생성할 테이블 쿼리들을 딕셔너리로 관리 (가독성 향상)
    tables_sql = {
        "HC_stock_master": """
            CREATE TABLE IF NOT EXISTS HC_stock_master (
                id            INT AUTO_INCREMENT PRIMARY KEY,
                ticker        VARCHAR(10) NOT NULL UNIQUE,
                stock_name    VARCHAR(100) NOT NULL,
                market_type   VARCHAR(10) NOT NULL,
                status        VARCHAR(20) DEFAULT 'ACTIVE',
                listed_date   DATE NULL,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        "HC_stock_minute1": """
            CREATE TABLE IF NOT EXISTS HC_stock_minute1 (
                id             BIGINT AUTO_INCREMENT PRIMARY KEY,
                ticker         VARCHAR(10) NOT NULL COMMENT '종목코드 (예: 005930)',
                stck_bsop_date DATE NOT NULL COMMENT '영업 일자 (YYYY-MM-DD)',
                stck_prpr      INT NOT NULL COMMENT '당일 최종 종가 (주식 현재가)',
                prdy_vrss      INT NOT NULL COMMENT '전일 대비 등락폭',
                prdy_ctrt      DECIMAL(5, 2) NOT NULL COMMENT '전일 대비 등락률',
                acml_vol       BIGINT NOT NULL COMMENT '당일 누적 거래량',
                acml_tr_pbmn   BIGINT NOT NULL COMMENT '당일 누적 거래대금',
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '시스템 데이터 적재 시간',
                UNIQUE KEY uq_ticker_date (ticker, stck_bsop_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='한국투자증권 output1 기준 당일 마감 일별 요약 테이블';
        """,
        "HC_stock_minute2": """
            CREATE TABLE IF NOT EXISTS HC_stock_minute2 (
                id             BIGINT AUTO_INCREMENT PRIMARY KEY,
                ticker         VARCHAR(10) NOT NULL COMMENT '종목코드 (예: 005930)',
                stck_bsop_date DATE NOT NULL COMMENT '영업 일자 (YYYY-MM-DD)',
                stck_cntg_hour TIME NOT NULL COMMENT '주식 체결 시간 / 분봉 시간 (HH:MM:SS)',
                stck_oprc      INT NOT NULL COMMENT '주식 시가 (해당 분 시작 가격)',
                stck_hgpr      INT NOT NULL COMMENT '주식 고가 (해당 분 최고 가격)',
                stck_lwpr      INT NOT NULL COMMENT '주식 저가 (해당 분 최저 가격)',
                stck_prpr      INT NOT NULL COMMENT '주식 현재가 / 종가 (해당 분 마감 가격)',
                cntg_vol       BIGINT NOT NULL COMMENT '체결 거래량 (해당 1분 동안 터진 거래량)',
                acml_tr_pbmn   BIGINT NOT NULL COMMENT '누적 거래대금 (당일 장 시작부터 해당 분까지의 누적치)',
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '시스템 데이터 적재 시간',
                UNIQUE KEY uq_ticker_date_time (ticker, stck_bsop_date, stck_cntg_hour)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='한국투자증권 output2 기준 1분 단위 분봉 적재 테이블';
        """,
        "HC_stock_hourly": """
            CREATE TABLE IF NOT EXISTS HC_stock_hour (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL COMMENT '종목코드 (예: 005930)',
                stck_bsop_date DATE NOT NULL COMMENT '영업 일자 (YYYY-MM-DD)',
                stck_cntg_hour TIME NOT NULL COMMENT '시간봉 기준 시간 (HH:00:00)',
                stck_oprc INT NOT NULL COMMENT '시간봉 시가',
                stck_hgpr INT NOT NULL COMMENT '시간봉 고가',
                stck_lwpr INT NOT NULL COMMENT '시간봉 저가',
                stck_prpr INT NOT NULL COMMENT '시간봉 종가',
                cntg_vol BIGINT NOT NULL COMMENT '시간봉 거래량',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '시스템 데이터 적재 시간',
                UNIQUE KEY uq_ticker_date_hour (
                    ticker,
                    stck_bsop_date,
                    stck_cntg_hour
                )
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='시간봉 적재 테이블';
        """
    }

    # 텍스트 리스트(딕셔너리 키/값)를 돌면서 공통 함수 호출
    for table_name, sql_query in tables_sql.items():
        print(f"[{table_name}] 테이블 생성 확인 중...")
        patchSingleRow(sql_query, "테이블 생성 실패")

    print("========= 모든 테이블 초기화 완료 =========")


if __name__ == "__main__":
    initialize_all_tables();