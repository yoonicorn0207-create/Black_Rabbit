import sys, os
from opensearchpy import OpenSearch

CODESET_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CODESET_DIR not in sys.path:
    sys.path.append(CODESET_DIR)

from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.abspath(os.path.join(current_dir, "..", "..", "dataset", "config", ".env"))
load_dotenv(dotenv_path=dotenv_path, override=True)

OS_HOST = os.getenv("OS_HOST", "localhost")
OS_PORT = int(os.getenv("OS_PORT", 9200))
OS_USER = os.getenv("OS_USER", "admin")
OS_PASSWORD = os.getenv("OS_PASSWORD")

# ======================= op 인덱스명= rdb 테이블명 =======================
INDEX_NAME = "news_stock_sentiment"


# ======================= op 연결 =======================
def get_client():
    return OpenSearch(
        hosts=[{"host": OS_HOST, "port": OS_PORT}],
        http_auth=(OS_USER, OS_PASSWORD),
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False,
    )


# ======================= 인덱스 필드= rdb 테이블 컬럼 =======================
INDEX_BODY = {
    "settings": {
        "index": {"knn": True}
    },
    "mappings": {
        "properties": {
            "news_id": {"type": "keyword"},        # 원본 기사 역추적용
            "ticker": {"type": "keyword"},
            "matched_name": {"type": "keyword"},    # stock_name -> matched_name
            "sector": {"type": "keyword"},
            "sentiment": {"type": "keyword"},
            "event_tags": {"type": "keyword"},
            "keywords": {"type": "keyword"},
            "importance": {"type": "float"},
            "published_at": {"type": "date"},       # 값은 pub_date에서 채움
            "title": {"type": "text"},
            "summary": {"type": "text"},
            "source": {"type": "keyword"},          # 언론사명
            "source_url": {"type": "keyword"},       # 값은 link에서 채움
            "embedding": {
                "type": "knn_vector",
                "dimension": 1024,   # bge-m3 임베딩 모델 기준
                "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimil",
                    "engine": "nmslib"
                }
            }
        }
    }
}


def create_index():
    client = get_client()
    if client.indices.exists(index=INDEX_NAME):
        print(f"인덱스 '{INDEX_NAME}' 이미 존재함")
        return
    client.indices.create(index=INDEX_NAME, body=INDEX_BODY)
    print(f"인덱스 '{INDEX_NAME}' 생성 완료")


if __name__ == "__main__":
    create_index()