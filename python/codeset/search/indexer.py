import sys, os
import json
import requests
from datetime import datetime

CODESET_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CODESET_DIR not in sys.path:
    sys.path.append(CODESET_DIR)

from dotenv import load_dotenv
from database import queryRows
from opensearchpy import OpenSearch, helpers


current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.abspath(os.path.join(current_dir, "..", "..", "dataset", "config", ".env"))
load_dotenv(dotenv_path=dotenv_path, override=True)

OS_HOST = os.getenv("OS_HOST", "localhost")
OS_PORT = int(os.getenv("OS_PORT", 9200))
OS_USER = os.getenv("OS_USER", "admin")
OS_PASSWORD = os.getenv("OS_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

INDEX_NAME = "news_stock_sentiment"

os_client = OpenSearch(
    hosts=[{"host": OS_HOST, "port": OS_PORT}],
    http_auth=(OS_USER, OS_PASSWORD),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
)


## ======================= 이미 색인된 문서 ID 조회 =======================
def get_existing_doc_ids():
    try:
        query = {"query": {"match_all": {}}, "_source": False, "size": 10000}
        res = os_client.search(index=INDEX_NAME, body=query, scroll="1m")
        scroll_id = res["_scroll_id"]
        ids = {hit["_id"] for hit in res["hits"]["hits"]}

        while True:
            res = os_client.scroll(scroll_id=scroll_id, scroll="1m")
            hits = res["hits"]["hits"]
            if not hits:
                break
            ids.update(hit["_id"] for hit in hits)

        return ids
    except Exception as e:
        print(f"기존 색인 ID 조회 실패 (인덱스가 비어있으면 정상): {e}")
        return set()



## ======================= 색인 대상 데이터 조립 =======================
def fetch_indexable_rows():
    sql = """
        SELECT m.id AS metadata_id, m.news_id, m.ticker, m.matched_name, m.sector,
               m.sentiment, m.event_tags, m.keywords, m.summary, m.importance,
               r.title, r.link, r.originallink, r.pub_date, r.source
        FROM HC_news_metadata m
        JOIN HC_news_raw r ON m.news_id = r.id
        WHERE m.ticker IS NOT NULL
    """
    return queryRows(sql, "색인 대상 조회 실패")


## ======================= 임베딩 생성 =======================
def get_embedding(text):
    res = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "bge-m3", "prompt": text}
    )
    return res.json()["embedding"]

def parse_json_field(value):
    if value is None:
        return []
    if isinstance(value, (list, dict)):
        return value
    return json.loads(value)


def format_date(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt.replace(" ", "T")
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


## ======================= bulk indexing =======================
def build_documents():
    rows = fetch_indexable_rows()
    existing_ids = get_existing_doc_ids()
    total = len(rows)
    skipped = 0

    print(f"색인 대상: {total}건 (기존 색인: {len(existing_ids)}건)")

    for idx, row in enumerate(rows, start=1):
        doc_id = str(row["metadata_id"])

        if doc_id in existing_ids:
            skipped += 1
            continue

        embedding_text = f"[{row['sector']}] {row['summary']}"
        embedding = get_embedding(embedding_text)

        doc = {
            "_index": INDEX_NAME,
            "_id": doc_id,
            "_source": {
                "news_id": row["news_id"],
                "ticker": row["ticker"],
                "matched_name": row["matched_name"],
                "sector": row["sector"],
                "sentiment": row["sentiment"],
                "event_tags": parse_json_field(row["event_tags"]),
                "keywords": parse_json_field(row["keywords"]),
                "importance": row["importance"],
                "published_at": format_date(row["pub_date"]),
                "title": row["title"],
                "summary": row["summary"],
                "source": row["source"],
                "source_url": row["originallink"] or row["link"],  # <- 변경: originallink 우선
                "embedding": embedding,
            }
        }
        print(f"[{idx}/{total}] {row['matched_name']} 임베딩 완료")
        yield doc

    print(f"신규 임베딩: {total - skipped}건 / 스킵: {skipped}건")


def run_indexing():
    success, errors = helpers.bulk(os_client, build_documents(), raise_on_error=False)
    print(f"\n색인 완료: 성공 {success}건")
    if errors:
        print(f"실패 {len(errors)}건")
        for e in errors[:5]:
            print(e)


## ======================= 인덱싱 검증 =======================
def search_sector_recommendation(sector="반도체", hours=24):
    from datetime import datetime, timedelta
    time_from = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S")

    query = {
        "query": {
            "bool": {
                "filter": [
                    {"term": {"sector": sector}},
                    {"term": {"sentiment": "positive"}},
                    {"range": {"published_at": {"gte": time_from}}}
                ]
            }
        },
        "sort": [{"importance": {"order": "desc"}}],
        "size": 10
    }

    res = os_client.search(index=INDEX_NAME, body=query)
    hits = res["hits"]["hits"]
    print(f"검색 결과: {len(hits)}건 (전체 매칭: {res['hits']['total']['value']}건)")
    for h in hits:
        src = h["_source"]
        print(f"- [{src['matched_name']}] {src['title']} (중요도: {src['importance']}, {src['published_at']})")

    return hits


## ======================= 기존 색인 문서의 source_url을 originallink로 일괄 정정 =======================
def fix_source_url_to_originallink():
    sql = """
        SELECT m.id AS metadata_id, r.link, r.originallink
        FROM HC_news_metadata m
        JOIN HC_news_raw r ON m.news_id = r.id
        WHERE m.ticker IS NOT NULL
    """
    rows = queryRows(sql, "정정 대상 조회 실패")

    fixed = 0
    for row in rows:
        doc_id = str(row["metadata_id"])
        correct_url = row["originallink"] or row["link"]
        try:
            os_client.update(index=INDEX_NAME, id=doc_id, body={"doc": {"source_url": correct_url}})
            fixed += 1
        except Exception as e:
            print(f"업데이트 실패 ({doc_id}): {e}")

    print(f"source_url 정정 완료: {fixed}건")


if __name__ == "__main__":
    # fix_source_url_to_originallink()  # 기존 데이터 정정 먼저 1회 실행
    run_indexing()
    search_sector_recommendation(sector="반도체")