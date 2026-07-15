import requests
import re
import time
import sys, os
import pandas as pd
import hashlib

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone


CODESET_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../codeset
if CODESET_DIR not in sys.path:
    sys.path.append(CODESET_DIR)

from common_api import getWatchlistByKeywords
from database import patchAllRows, queryRows


current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
dotenv_path = os.path.abspath(os.path.join(current_dir, "..", "..", "dataset", "config", ".env"))
load_dotenv(dotenv_path=dotenv_path, override=True)

CLIENT_ID = os.getenv("NAVER_CLIENT_KEY")
CLIENT_SECRET = os.getenv("NAVER_SECRET_KEY")

HEADERS = {"User-Agent": "Mozilla/5.0"}


# ======================= 로직 흐름 =======================
# 뉴스 API 호출
# 조건에 맞는 기사 필터링
# 뉴스 수집 파이프라인
# 데이터 정제
# DB 저장

# ======================= 뉴스 리스트 호출 api =======================
def search_naver_news(query, display=100, start=1, sort="date"):
    # query 검색어
    # display 최대 100
    # start  최대 1000
    # sort 정확도- sim, 최신순- date

    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
    }
    params = {
        "query": query, # 검색어
        "display": display, # 최대 100
        "start": start,  # 최대 1000
        "sort": sort # 정확도- sim, 최신순- date
    }
    res = requests.get(url, headers=headers, params=params, timeout=5)
    res.raise_for_status()
    #t itle(HTML <b> 태그 포함),
    # originallink(언론사 원문),
    # link(네이버뉴스 링크, 보통 n.news.naver.com),
    # description, p
    # ubDate
    return res.json()["items"]


## ======================= 최근 24시간 내 작성 기사만 크롤링 하기 위해 필터 로직 =======================
def is_recent(pub_date_str, hours=24):
    pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
    return pub_date >= datetime.now(timezone.utc).astimezone() - timedelta(hours=hours)


## ============================ 금융과 관련된 키워드 필터링 ============================
def is_finance_related(title, description):
    # 이부분이 없으면 두산/ LG 등 야구팀이나 가전제품 기사까지 걸림
    FINANCE_KEYWORDS = ["주가", "실적", "매출", "영업이익", "목표주가", "증권", "코스피", "코스닥", "투자의견", "공시"]

    text = title + description
    return any(kw in text for kw in FINANCE_KEYWORDS)


def clean_title(raw):
    return re.sub(r"<.*?>|&quot;|&amp;", "", raw)


# ======================= 뉴스 리스트 호출 api =======================
def collect_news():
    WATCHLIST = getWatchlistByKeywords(["반도체", "전자부품", "정밀기기"])

    seen = set()
    all_items = []

    for name in WATCHLIST:
        items = search_naver_news(name, display=30, sort="date")
        for it in items:
            key = it["link"]
            if key in seen:
                continue

            if not is_finance_related(it["title"], it["description"]):
                continue  # <-- 여기서 야구/일반뉴스 등 걸러냄

            if not is_recent(it["pubDate"]):
                continue  # <-- 작성된지 24시간 내의 기사 필터링

            seen.add(key)
            it["title"] = clean_title(it["title"])
            it["matched_stock"] = name
            all_items.append(it)
        time.sleep(0.2)
    return all_items


# ======================= 본문 크롤링+ 정제 =======================
def clean_body(text):
    patterns = [
        r"\S+@\S+\.(com|co\.kr|net)",              # 이메일
        r"[가-힣]{2,4}\s*기자",                      # 기자 서명
        r"무단[\s\S]{0,10}전재[\s\S]{0,20}금지",       # 저작권 문구
        r"\[?사진\s*[=:]?\s*[가-힣A-Za-z\s]+\]?",     # 사진 캡션
        r"Copyright.*",                             # 저작권 라인
    ]
    for p in patterns:
        text = re.sub(p, "", text)
    text = re.sub(r"\n{2,}", "\n", text).strip()
    return text


def fetch_body(url):
    res = requests.get(url, headers=HEADERS, timeout=5)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    body = soup.select_one("#dic_area") or soup.select_one("#newsct_article")
    if not body:
        return None
    # 기사 안 이미지 캡션, 관련기사 박스 제거
    for tag in body.select(".end_photo_org, .ad_wrap, .vod_player_wrap"):
        tag.decompose()
    text = body.get_text("\n", strip=True)
    text = re.sub(r"\S+@\S+\.(com|co\.kr|net)", "", text)  # 기자 이메일
    text = re.sub(r"\n{2,}", "\n", text)
    return clean_body(text.strip())


## ============================ 네이버 api 호출하여 뉴스 받아오기 ============================
def collect_news_with_body():
    items = collect_news()
    total = len(items)
    results = []
    skipped_domains = {}

    for idx, it in enumerate(items, start=1):
        link = it["link"]
        domain = urlparse(link).netloc

        print(f"[{idx}/{total}] {it['matched_stock']} - {it['title'][:30]}...")

        # n.news.naver.com 계열만 우선 처리 (셀렉터가 고정이라 안전)
        if "naver.com" not in domain:
            skipped_domains[domain] = skipped_domains.get(domain, 0) + 1
            print(f"    -> 스킵 (도메인: {domain})")
            continue

        body = fetch_body(link)
        if not body:
            print("    -> 본문 파싱 실패")
            continue

        it["body"] = body
        results.append(it)
        print(f"    -> 본문 확보 ({len(body)}자)")
        time.sleep(0.2)

    print(f"\n본문 확보: {len(results)}건 / 전체 {total}건")
    if skipped_domains:
        print("스킵된 도메인 (언론사 원문 직행, 아직 파서 미대응):")
        for domain, count in sorted(skipped_domains.items(), key=lambda x: -x[1]):
            print(f"  {domain}: {count}건")

    return results


## ============================ 크롤링한 뉴스 raw data db 저장하기 ============================
def make_article_hash(title, body):
    normalized = re.sub(r"\s+", "", title + body)  # 공백 다 제거하고 합침
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def parse_pub_date(pub_date_str):
    try:
        dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


def save_news_to_db(news_items):
    sql = """
        INSERT INTO HC_news_raw (link, originallink, title, description, body, matched_stock, pub_date, article_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            body = VALUES(body),
            title = VALUES(title)
    """
    data = [
        (
            it["link"], it.get("originallink"), it["title"], it.get("description"),
            it.get("body"), it["matched_stock"], parse_pub_date(it.get("pubDate")),
            make_article_hash(it["title"], it.get("body"))
        )
        for it in news_items
    ]
    patchAllRows(sql, data, "뉴스 원본 저장 실패")


# ======================= 종목+섹터 마스터 데이터 가져오기 =======================
def getSectorMasterList():
    """ 이미 DB에 저장된 마스터 데이터를 종목명 리스트로 반환 (뉴스 검색용) """
    rows = queryRows("SELECT * FROM HC_stock_master WHERE sector IS NOT NULL", "종목 마스터 조회 실패")
    return [row["name"] for row in rows]


def get_krx_corp_list():
    url = "http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13"
    df = pd.read_html(url, header=0, encoding="euc-kr")[0]
    df["종목코드"] = df["종목코드"].astype(str).str.zfill(6)
    return df[["회사명", "종목코드", "업종", "주요제품"]]


def load_krx_master_to_db():
    df = get_krx_corp_list()
    df.columns = ["name", "ticker", "industry", "products"]

    sql = """
        UPDATE HC_stock_master
        SET industry = %s
        WHERE ticker = %s
    """
    data = [(row.industry, row.ticker) for row in df.itertuples(index=False)]
    patchAllRows(sql, data, "종목 업종 업데이트 실패")


## ======================= 임시 반도체 섹터 삽입 함수 =======================
def apply_sector_mapping():
    INDUSTRY_TO_SECTOR = {
        "반도체 제조업": "전기·전자",
        "전자부품 제조업": "전기·전자",
        "통신 및 방송 장비 제조업": "전기·전자",
        "컴퓨터 및 주변장치 제조업": "전기·전자",
        "기타 전기장비 제조업": "전기·전자",
        "가전제품 및 정보통신장비 소매업": "전기·전자",
        "측정, 시험, 항해, 제어 및 기타 정밀기기 제조업; 광학기기 제외": "기계·장비",
        "전동기, 발전기 및 전기 변환 · 공급 · 제어 장치 제조업": "기계·장비",
        "전기업": "전기가스업",
        "전기 통신업": "통신업",
        "전기 및 통신 공사업": "통신업",
        "소프트웨어 개발 및 공급업": "서비스업",
        "컴퓨터 프로그래밍, 시스템 통합 및 관리업": "서비스업",
        "자료처리, 호스팅, 포털 및 기타 인터넷 정보매개 서비스업": "서비스업",
    }

    sql = """
        UPDATE HC_stock_master
        SET sector = %s
        WHERE industry = %s
    """
    data = [(sector, industry) for industry, sector in INDUSTRY_TO_SECTOR.items()]
    patchAllRows(sql, data, "섹터 매핑 업데이트 실패")


if __name__ == "__main__":
    news = collect_news_with_body()
    print(news[0] if news else "결과 없음")
    save_news_to_db(news)