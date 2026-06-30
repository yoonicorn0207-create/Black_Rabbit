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
                id                BIGINT AUTO_INCREMENT PRIMARY KEY,
                ticker            VARCHAR(10) NOT NULL COMMENT '종목코드',
                stck_bsop_date    DATE NOT NULL COMMENT '영업 일자 (YYYY-MM-DD)',
                stck_prpr         INT NOT NULL COMMENT '주식 현재가',
                prdy_vrss         INT NOT NULL COMMENT '전일 대비 변동폭',
                prdy_vrss_sign    VARCHAR(1) COMMENT '전일 대비 부호',
                prdy_ctrt         DECIMAL(10, 2) NOT NULL COMMENT '전일 대비율',
                stck_prdy_clpr    INT NOT NULL COMMENT '전일 대비 종가',
                acml_vol          BIGINT NOT NULL COMMENT '누적 거래량',
                acml_tr_pbmn      BIGINT NOT NULL COMMENT '누적 거래대금',
                hts_kor_isnm      VARCHAR(40) COMMENT '한글 종목명',
                created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '시스템 데이터 적재 시간',
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
        """,
        "HC_user": """
            CREATE TABLE IF NOT EXISTS HC_user (
                id                 BIGINT AUTO_INCREMENT PRIMARY KEY,
                username           VARCHAR(30) NOT NULL COMMENT '로그인 아이디',
                password_hash      VARCHAR(255) NOT NULL COMMENT 'BCrypt 해시 비밀번호',
                email              VARCHAR(100) NOT NULL COMMENT '이메일',
                balance            BIGINT NOT NULL DEFAULT 0 COMMENT '예수금',
                role               ENUM('USER', 'ADMIN')
                                       NOT NULL DEFAULT 'USER'
                                       COMMENT '회원 권한',
                status             ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED', 'DELETED')
                                       NOT NULL DEFAULT 'ACTIVE'
                                       COMMENT '회원 상태',
                email_verified     BOOLEAN NOT NULL DEFAULT FALSE COMMENT '이메일 인증 여부',
                last_login_at      TIMESTAMP NULL COMMENT '마지막 로그인 시간',
                created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '가입일',
                updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                                       ON UPDATE CURRENT_TIMESTAMP
                                       COMMENT '회원정보 수정일',
                deleted_at         TIMESTAMP NULL COMMENT '탈퇴일',
                UNIQUE KEY uq_username (username),
                UNIQUE KEY uq_email (email)

            ) ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COMMENT='회원 정보';
        """,
        "HC_refresh_token": """
            CREATE TABLE IF NOT EXISTS HC_refresh_token (
                id                      BIGINT AUTO_INCREMENT PRIMARY KEY,
                user_id                 BIGINT NOT NULL COMMENT '회원 PK',
                refresh_token_hash      VARCHAR(255) NOT NULL COMMENT 'Refresh Token 해시값',
                expires_at              TIMESTAMP NOT NULL COMMENT '토큰 만료시간',
                created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                                            COMMENT '발급시간',
                CONSTRAINT fk_refresh_token_user
                    FOREIGN KEY (user_id)
                    REFERENCES HC_user(id)
                    ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_expires_at (expires_at),
                UNIQUE KEY uq_refresh_token (refresh_token_hash)
            ) ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COMMENT='Refresh Token';
        """,
        "HC_user_holdings": """
            CREATE TABLE HC_user_holdings (
                holding_id BIGINT AUTO_INCREMENT PRIMARY KEY, 
                user_id VARCHAR(50) NOT NULL,                 
                stck_shrn_iscd VARCHAR(10) NOT NULL,          
                total_quantity INT DEFAULT 0,                 
                total_buy_amount DECIMAL(19, 4) DEFAULT 0,    
                avg_buy_price DECIMAL(19, 4) DEFAULT 0,       
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
                -- CONSTRAINT 앞에 쉼표(,)가 있어야 합니다.
                CONSTRAINT fk_user_holdings_user 
                    FOREIGN KEY (user_id) REFERENCES HC_user(id) 
                    ON DELETE CASCADE
            )ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COMMENT='HC_user_holdings';; -- 마지막에 닫는 괄호와 세미콜론 필수                
        """
    }

    # 텍스트 리스트(딕셔너리 키/값)를 돌면서 공통 함수 호출
    for table_name, sql_query in tables_sql.items():
        print(f"[{table_name}] 테이블 생성 확인 중...")
        patchSingleRow(sql_query, "테이블 생성 실패")

    print("========= 모든 테이블 초기화 완료 =========")


if __name__ == "__main__":
    initialize_all_tables();