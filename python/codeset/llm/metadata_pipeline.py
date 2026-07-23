import sys, os
import json
import requests
import time
import re

from datetime import datetime
from pydantic import BaseModel, ValidationError
from typing import List
from difflib import get_close_matches
from dotenv import load_dotenv

CODESET_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../codeset
if CODESET_DIR not in sys.path:
    sys.path.append(CODESET_DIR)

from database import patchSingleRow, patchAllRows, queryRows


current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
dotenv_path = os.path.abspath(os.path.join(current_dir, "..", "..", "dataset", "config", ".env"))
load_dotenv(dotenv_path=dotenv_path, override=True)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_URL = os.getenv("OLLAMA_URL")
CJK_PATTERN = re.compile(r'[\u4e00-\u9fff]')  # 한자(중국어) 유니코드 범위
_ALL_STOCKS_CACHE = None

_session = requests.Session()  # 커넥션 재사용


## ======================= pydantic 스키마 =======================
class ArticleMetadata(BaseModel):
    stocks: List[str]
    sector: str
    event_tags: List[str]
    keywords: List[str]
    summary: str
    sentiment: str
    importance: float


SYSTEM_PROMPT = """너는 한국 증권 뉴스 기사에서 메타데이터를 추출하는 어시스턴트다.
반드시 아래 JSON 스키마와 정확히 일치하는 순수 JSON만 출력해라. 설명이나 코드블록 없이 JSON만.

{
  "stocks": ["회사명1", "회사명2"],
  "sector": "업종명",
  "event_tags": ["실적", "목표주가"],
  "keywords": ["키워드1", "키워드2"],
  "summary": "2문장 이내 요약",
  "sentiment": "positive|negative|neutral",
  "importance": 0.0~1.0 사이 숫자
}"""


## ======================= 중국어 검사 =======================
def contains_broken_language(value):
    """문자열이든 리스트든 재귀적으로 검사"""
    if isinstance(value, str):
        return bool(CJK_PATTERN.search(value))
    if isinstance(value, list):
        return any(contains_broken_language(v) for v in value)
    return False


def is_metadata_clean(metadata: ArticleMetadata) -> bool:
    fields_to_check = [
        metadata.stocks, metadata.sector, metadata.event_tags,
        metadata.keywords, metadata.summary
    ]
    return not any(contains_broken_language(f) for f in fields_to_check)


def parse_json_field(value):
    if value is None:
        return []
    if isinstance(value, (list, dict)):
        return value  # 이미 파싱된 상태
    return json.loads(value)


## ======================= 종목명 검사- 오염된 종목명 출력 =======================
# 한글 자모만 추출해서 비교 (영문/기호 다 무시)
def extract_hangul(text):
    return re.sub(r'[^가-힣]', '', text)


## ======================= 전체 종목 캐싱 (반복 조회 방지) =======================
def get_all_stocks_cached():
    global _ALL_STOCKS_CACHE
    if _ALL_STOCKS_CACHE is None:
        _ALL_STOCKS_CACHE = queryRows("SELECT ticker, stock_name FROM HC_stock_master", "전체 종목 조회 실패")
    return _ALL_STOCKS_CACHE




## ======================= DB에서 미처리 기사 가져오기 =======================
def get_unprocessed_articles(limit=None):
    try:
        sql = """SELECT id, title, body FROM HC_news_raw
            WHERE processed = FALSE AND body IS NOT NULL AND metadata_attempts < 3"""

        if limit:
            sql += f" LIMIT {int(limit)}"
        return queryRows(sql, "미처리 기사 조회 실패")
    except Exception as e:
        print(e)
        return []



## ======================= 깨진 종목명 검사 =======================
def is_valid_stock_name(name):
    # 한자(CJK 통합 한자) 섞인 이름은 깨진 걸로 간주
    if re.search(r'[\u4e00-\u9fff]', name):
        return False
    # 최소한의 형태 체크 (한글/영문/숫자만 허용)
    if not re.match(r'^[가-힣A-Za-z0-9&\.\s]+$', name):
        return False
    return True



## ======================= Ollama 호출 + 검증/재시도 =======================
def extract_metadata(title, body, max_retry=2):
    article_text = f"제목: {title}\n본문: {body[:1500]}"

    for attempt in range(max_retry + 1):
        try:
            res = _session.post(OLLAMA_URL, json={
                "model": OLLAMA_MODEL,
                "format": "json",
                "stream": False,
                "options": {"temperature": 0.1}, ## 언어 혼입 현상으로 추가
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": article_text}
                ]
            }, timeout=60)
            raw = res.json()["message"]["content"]
            data = json.loads(raw)
            metadata = ArticleMetadata(**data)

            if not is_metadata_clean(metadata):
                print(f"    [재시도 {attempt + 1}/{max_retry+1}] 언어 오염 감지, 재시도")
                continue

            return metadata

        except (
            json.JSONDecodeError,
            ValidationError,
            requests.RequestException,
            KeyError,
            TypeError
        ) as e:
            print(f"    [재시도 {attempt+1}/{max_retry}] 실패: {e}")
            continue

    return None


## ======================= 종목명 -> ticker 매칭 =======================
def match_stock_ticker(name):
    try:
        rows = queryRows(
            "SELECT ticker FROM HC_stock_master WHERE stock_name = %s LIMIT 1",
            "종목 정확매칭 실패", (name,)
        )
        if rows:
            return rows[0]["ticker"]

        # 정확매칭 실패시 부분매칭 (LLM이 "하이닉스"처럼 줄여서 줄 때 대비)
        rows = queryRows(
            "SELECT ticker FROM HC_stock_master WHERE stock_name LIKE %s LIMIT 1",
            "종목 부분매칭 실패", (f"%{name}%",)
        )
        if rows:
            return rows[0]["ticker"]

        # 한글만 남겨서 마스터 종목명과 비교 (변형된 영문/기호 무시)
        hangul_only = extract_hangul(name)
        if len(hangul_only) >= 2:
            all_stocks = get_all_stocks_cached()

            for stock in all_stocks:
                if extract_hangul(stock["stock_name"]) == hangul_only:
                    return stock["ticker"]

        return None
    except Exception as e:
        print(e)
        return None


## ======================= 메타데이터 저장 + processed 갱신 =======================
def save_metadata(news_id, metadata: ArticleMetadata):
    try:
        rows_to_insert = []
        for stock_name in metadata.stocks:
            if not is_valid_stock_name(stock_name):
                print(f"    [경고] 깨진 종목명 스킵: {stock_name}")
                continue

            ticker = match_stock_ticker(stock_name)
            rows_to_insert.append((
                news_id, ticker, stock_name, metadata.sector,
                json.dumps(metadata.event_tags, ensure_ascii=False),
                json.dumps(metadata.keywords, ensure_ascii=False),
                metadata.summary, metadata.sentiment, metadata.importance
            ))

        if rows_to_insert:
            sql = """
                INSERT INTO HC_news_metadata
                    (news_id, ticker, matched_name, sector, event_tags, keywords, summary, sentiment, importance)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            patchAllRows(sql, rows_to_insert, "메타데이터 저장 실패")

        patchSingleRow(
            "UPDATE HC_news_raw SET processed = TRUE WHERE id = %s",
            "processed 플래그 갱신 실패", (news_id,)
        )
        return True
    except Exception as e:
        print(e)
        return False


## ======================= 배치 실행기 =======================
def run_pipeline(limit=None):
    start_time = time.time()
    start_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[시작] {start_dt}")

    articles = get_unprocessed_articles(limit)
    total = len(articles)
    print(f"처리 대상: {total}건")

    success, failed = 0, 0
    for idx, article in enumerate(articles, start=1):

        try:
            article_start = time.time()
            print(f"[{idx}/{total}] news_id={article['id']} - {article['title'][:30]}...")

            metadata = extract_metadata(article["title"], article["body"])
            if metadata is None:
                print(f"    -> 추출 실패, 스킵 ({time.time() - article_start:.1f}초)")
                patchSingleRow(
                        "UPDATE HC_news_raw SET metadata_attempts = metadata_attempts + 1 WHERE id = %s",
                        "실패 카운트 갱신 실패", (article["id"],)
                )
                failed += 1
                continue

            saved = save_metadata(article["id"], metadata)
            if not saved:
                print(f"    -> 저장 실패, 스킵 ({time.time() - article_start:.1f}초)")
                failed += 1
                continue

            print(f"    -> 저장 완료 ({time.time() - article_start:.1f}초, 종목: {metadata.stocks}, 감성: {metadata.sentiment})")
            success += 1

        except Exception as e:
            print(f"    -> [예상치 못한 에러] {e}")
            failed += 1
            continue

    end_time = time.time()
    end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elapsed = end_time - start_time

    print(f"\n[종료] {end_dt}")
    print(f"완료: 성공 {success}건 / 실패 {failed}건 / 전체 {total}건")
    print(f"총 소요시간: {elapsed:.1f}초 ({elapsed/60:.1f}분)")
    if total > 0:
        print(f"건당 평균: {elapsed/total:.1f}초")


## ======================= db에 저장된 깨진 데이터 정리 =======================
def audit_and_clean_metadata():
    rows = queryRows(
        "SELECT id, news_id, matched_name, sector, event_tags, keywords, summary FROM HC_news_metadata",
        "메타데이터 전체 조회 실패"
    )

    broken_ids = []
    broken_news_ids = set()

    for row in rows:
        fields = [
            row["matched_name"], row["sector"],
            parse_json_field(row["event_tags"]),
            parse_json_field(row["keywords"]),
            row["summary"],   # <- 추가
        ]
        if any(contains_broken_language(f) for f in fields):
            broken_ids.append(row["id"])
            broken_news_ids.add(row["news_id"])

    print(f"오염된 메타데이터 로우: {len(broken_ids)}건 / 관련 기사: {len(broken_news_ids)}건")

    if not broken_ids:
        return

    # 오염된 메타데이터 삭제
    placeholders = ",".join(["%s"] * len(broken_ids))
    patchSingleRow(
        f"DELETE FROM HC_news_metadata WHERE id IN ({placeholders})",
        "오염 메타데이터 삭제 실패", tuple(broken_ids)
    )

    # 해당 기사들 재처리 대상으로 되돌림
    news_id_list = list(broken_news_ids)
    placeholders2 = ",".join(["%s"] * len(news_id_list))
    patchSingleRow(
        f"UPDATE HC_news_raw SET processed = FALSE WHERE id IN ({placeholders2})",
        "processed 초기화 실패", tuple(news_id_list)
    )

    print(f"재처리 대상으로 {len(news_id_list)}건 기사 초기화 완료")



if __name__ == "__main__":
    # 오염된 상태로 db에 저장된 데이터 processed-False로 되돌리기
    # audit_and_clean_metadata()

    run_pipeline()