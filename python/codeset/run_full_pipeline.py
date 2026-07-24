import sys, os
import time
from datetime import datetime

CODESET_DIR = os.path.dirname(os.path.abspath(__file__))
NAVER_DIR = os.path.join(CODESET_DIR, "naver")
LLM_DIR = os.path.join(CODESET_DIR, "llm")
SEARCH_DIR = os.path.join(CODESET_DIR, "search")

for p in (NAVER_DIR, LLM_DIR, SEARCH_DIR):
    if p not in sys.path:
        sys.path.append(p)

from search_news import collect_news_with_body, save_news_to_db
from metadata_pipeline import run_pipeline
from indexer import run_indexing

LOCK_FILE = os.path.join(CODESET_DIR, ".pipeline.lock")


def is_locked():
    if not os.path.exists(LOCK_FILE):
        return False
    # 락 파일이 2시간 넘게 방치돼있으면 죽은 프로세스로 간주하고 무시 (안전장치)
    age = time.time() - os.path.getmtime(LOCK_FILE)
    if age > 7200:
        print("[경고] 오래된 락 파일 감지, 무시하고 진행")
        return False
    return True


def acquire_lock():
    with open(LOCK_FILE, "w") as f:
        f.write(str(time.time()))


def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


def run_full_pipeline():
    if is_locked():
        print(f"[{datetime.now()}] 이전 실행이 아직 진행 중으로 보여 스킵")
        return

    acquire_lock()
    start = time.time()
    print(f"\n{'='*50}\n[전체 파이프라인 시작] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*50}")

    try:
        print("\n--- 1. 크롤링 ---")
        try:
            news = collect_news_with_body()
            save_news_to_db(news)
        except Exception as e:
            print(f"[크롤링 단계 실패] {e}")

        print("\n--- 2. 메타데이터 추출 ---")
        try:
            run_pipeline()
        except Exception as e:
            print(f"[메타데이터 추출 단계 실패] {e}")

        print("\n--- 3. 임베딩 + OpenSearch 색인 ---")
        try:
            run_indexing()
        except Exception as e:
            print(f"[색인 단계 실패] {e}")

    finally:
        release_lock()
        elapsed = time.time() - start
        print(f"\n[전체 파이프라인 종료] 총 소요시간: {elapsed:.1f}초 ({elapsed/60:.1f}분)")


if __name__ == "__main__":
    run_full_pipeline()