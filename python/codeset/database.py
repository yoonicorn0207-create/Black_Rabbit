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
        db=os.getenv("DB_NAME", "ai_analyzer"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
