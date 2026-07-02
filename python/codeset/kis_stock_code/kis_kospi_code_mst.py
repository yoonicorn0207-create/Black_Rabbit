import os
import ssl
import zipfile
import urllib.request
import io
import pandas as pd


def get_market_master_dataframe(market="kospi", base_dir=None, verbose=False):
    """
    한국투자증권 마스터 파일을 다운로드하여 데이터프레임으로 반환합니다.
    :param market: "kospi" 또는 "kosdaq"
    :param base_dir: 파일이 다운로드될 임시 디렉토리
    :param verbose: 진행 상황 출력 여부
    """
    if base_dir is None:
        base_dir = os.getcwd()

    market = market.lower()
    if market not in ["kospi", "kosdaq"]:
        raise ValueError("market 인자는 'kospi' 또는 'kosdaq'이어야 합니다.")

    # 1. 시장별 API 다운로드 주소 및 파일명 설정
    if market == "kospi":
        url = "https://new.real.download.dws.co.kr/common/master/kospi_code.mst.zip"
        zip_name = "kospi_code.zip"
        mst_name = "kospi_code.mst"
        split_byte = 228  # 코스피는 끝에서 228바이트 분할
    else:
        url = "https://new.real.download.dws.co.kr/common/master/kosdaq_code.mst.zip"
        zip_name = "kosdaq_code.zip"
        mst_name = "kosdaq_code.mst"
        split_byte = 222  # 코스닥은 끝에서 222바이트 분할

    ssl._create_default_https_context = ssl._create_unverified_context
    zip_path = os.path.join(base_dir, zip_name)
    mst_path = os.path.join(base_dir, mst_name)

    if verbose: print(f"[{market.upper()}] Downloading master file...")
    urllib.request.urlretrieve(url, zip_path)

    with zipfile.ZipFile(zip_path, 'r') as code_zip:
        code_zip.extractall(base_dir)

    if os.path.exists(zip_path):
        os.remove(zip_path)

    # 2. 메모리 버퍼 준비 (임시 파일 생성 안 함)
    part1_data = io.StringIO()
    part2_data = io.StringIO()

    if verbose: print(f"[{market.upper()}] Parsing file...")
    with open(mst_path, mode="r", encoding="cp949", errors='ignore') as f:
        for row in f:
            rf1 = row[0:len(row) - split_byte]
            rf1_1 = rf1[0:9].rstrip()
            rf1_2 = rf1[9:21].rstrip()
            rf1_3 = rf1[21:].strip()

            part1_data.write(f"{rf1_1},{rf1_2},{rf1_3}\n")

            rf2 = row[-split_byte:]
            part2_data.write(rf2)

    part1_data.seek(0)
    part2_data.seek(0)

    # 3. 데이터프레임 파싱 및 머지
    part1_columns = ['단축코드', '표준코드', '한글명' if market == "kospi" else '한글종목명']
    df1 = pd.read_csv(part1_data, header=None, names=part1_columns, encoding='cp949')

    # 시장별 전용 필드 규격 정의
    if market == "kospi":
        field_specs = [
            2, 1, 4, 4, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 9, 5, 5, 1, 1, 1, 2, 1, 1, 1, 2, 2, 2, 3, 1, 3, 12, 12,
            8, 15, 21, 2, 7, 1, 1, 1, 1, 1, 9, 9, 9, 5, 9, 8, 9, 3, 1, 1, 1
        ]
        part2_columns = [
            '그룹코드', '시가총액규모', '지수업종대분류', '지수업종중분류', '지수업종소분류', '제조업', '저유동성',
            '지배구조지수종목', 'KOSPI200섹터업종', 'KOSPI100', 'KOSPI50', 'KRX', 'ETP', 'ELW발행',
            'KRX100', 'KRX자동차', 'KRX반도체', 'KRX바이오', 'KRX은행', 'SPAC', 'KRX에너지화학',
            'KRX철강', '단기과열', 'KRX미디어통신', 'KRX건설', 'Non1', 'KRX증권', 'KRX선박',
            'KRX섹터_보험', 'KRX섹터_운송', 'SRI', '기준가', '매매수량단위', '시간외수량단위', '거래정지',
            '정리매매', '관리종목', '시장경고', '경고예고', '불성실공시', '우회상장', '락구분', '액면변경',
            '증자구분', '증거금비율', '신용가능', '신용기간', '전일거래량', '액면가', '상장일자', '상장주수',
            '자본금', '결산월', '공모가', '우선주', '공매도과열', '이상급등', 'KRX300', 'KOSPI', '매출액',
            '영업이익', '경상이익', '당기순이익', 'ROE', '기준년월', '시가총액', '그룹사코드', '회사신용한도초과',
            '담보대출가능', '대주가능'
        ]
    else:
        field_specs = [
            2, 1, 4, 4, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 9, 5, 5, 1, 1, 1, 2, 1, 1, 1, 2, 2, 2, 3, 1, 3, 12, 12, 8, 15, 21, 2,
            7, 1, 1, 1, 1, 9, 9, 9, 5, 9, 8, 9, 3, 1, 1, 1
        ]
        part2_columns = [
            '증권그룹구분코드', '시가총액 규모 구분 코드 유가', '지수업종 대분류 코드', '지수 업종 중분류 코드',
            '지수업종 소분류 코드', '벤처기업 여부 (Y/N)', '저유동성종목 여부', 'KRX 종목 여부', 'ETP 상품구분코드',
            'KRX100 종목 여부 (Y/N)', 'KRX 자동차 여부', 'KRX 반도체 여부', 'KRX 바이오 여부', 'KRX 은행 여부',
            '기업인수목적회사여부', 'KRX 에너지 화학 여부', 'KRX 철강 여부', '단기과열종목구분코드', 'KRX 미디어 통신 여부',
            'KRX 건설 여부', '(코스닥)투자주의환기종목여부', 'KRX 증권 구분', 'KRX 선박 구분', 'KRX섹터지수 보험여부',
            'KRX섹터지수 운송여부', 'KOSDAQ150지수여부 (Y,N)', '주식 기준가', '정규 시장 매매 수량 단위',
            '시간외 시장 매매 수량 단위', '거래정지 여부', '정리매매 여부', '관리 종목 여부', '시장 경고 구분 코드',
            '시장 경고위험 예고 여부', '불성실 공시 여부', '우회 상장 여부', '락구분 코드', '액면가 변경 구분 코드',
            '증자 구분 코드', '증거금 비율', '신용주문 가능 여부', '신용기간', '전일 거래량', '주식 액면가',
            '주식 상장 일자', '상장 주수(천)', '자본금', '결산 월', '공모 가격', '우선주 구분 코드',
            '공매도과열종목여부', '이상급등종목여부', 'KRX300 종목 여부 (Y/N)', '매출액', '영업이익', '경상이익',
            '단기순이익', 'ROE(자기자본이익률)', '기준년월', '전일기준 시가총액 (억)', '그룹사 코드',
            '회사신용한도초과여부', '담보대출가능여부', '대주가능여부'
        ]

    df2 = pd.read_fwf(part2_data, widths=field_specs, names=part2_columns)
    df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)

    # 4. 잔여 마스터 파일 깔끔하게 정리
    if os.path.exists(mst_path):
        os.remove(mst_path)

    # '단축코드' 필드의 KIS 접두사 'A' 제거 공통 처리
    df['단축코드'] = df['단축코드'].str.replace('A', '')

    if verbose: print(f"[{market.upper()}] Processed successfully.")
    return df


# 사용 예시
if __name__ == "__main__":
    # 코스피 가져오기
    df_kospi = get_market_master_dataframe(market="kospi", verbose=True)
    df_kospi.to_excel('kospi_code.xlsx', index=False)

    # 코스닥 가져오기
    df_kosdaq = get_market_master_dataframe(market="kosdaq", verbose=True)
    df_kosdaq.to_excel('kosdaq_code.xlsx', index=False)