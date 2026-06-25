import pymysql
import os
from dotenv import load_dotenv

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