import pymysql
import os
from dotenv import load_dotenv


load_dotenv(dotenv_path="../dataset/config/.env")


## =========== DB 연결 =================
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


## =========== execute =================
def patchSingleRow(sql, errorMsg, params=None ):
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"DB 실패 : {errorMsg} {e}")
        raise

    finally:
        conn.close()


## =========== executemany =================
def patchAllRows(sql, data, errorMsg):
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.executemany(sql, data)
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"DB 실패 : {errorMsg} {e}")
        raise

    finally:
        conn.close()


## =========== fetchall =================
def queryRows(sql,errorMsg, params=None):
    """ SQL을 실행하고 결과를 리스트(딕셔너리 형태)로 반환하는 공통 조회 함수 """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            patchSingleRow(sql, errorMsg, params)

            return cursor.fetchall() # 조회 결과 반환
    except Exception as e:
        print(f"DB 조회 실패: {e}")
        raise
    finally:
        conn.close()