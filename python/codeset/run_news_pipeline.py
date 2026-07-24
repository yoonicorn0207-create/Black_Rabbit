import sys, os

CODESET_DIR = os.path.dirname(os.path.abspath(__file__))
NAVER_DIR = os.path.join(CODESET_DIR, "naver")
LLM_DIR = os.path.join(CODESET_DIR, "llm")

for p in (NAVER_DIR, LLM_DIR):
    if p not in sys.path:
        sys.path.append(p)

from search_news import collect_news_with_body, save_news_to_db
from metadata_pipeline import run_pipeline


def crawl_and_extract():
    print("=== 크롤링 시작 ===")
    try:
        news = collect_news_with_body()
        save_news_to_db(news)
    except Exception as e:
        print(f"[크롤링 단계 실패] {e}")
        return  # 크롤링 실패하면 메타데이터 추출도 의미 없으니 여기서 종료

    print("=== 메타데이터 추출 시작 ===")
    try:
        run_pipeline()
    except Exception as e:
        print(f"[메타데이터 추출 단계 실패] {e}")


if __name__ == "__main__":
    crawl_and_extract()


## 매일 30분 주기로 실행되는 코드이며
## ai종목에 관련된 기사들을 크롤링 하여 rdb에 저장한 뒤
## ollama qwen2.5:7b-instruct 모델을 사용하여 메타데이터를 추출 및 가공하여 rdb 저장