import os
import ssl
import zipfile
import urllib.request
import io
import pandas as pd


def get_kosdaq_master_dataframe(base_dir=None, verbose=False):
    if base_dir is None:
        base_dir = os.getcwd()

    # 1. SSL 인증서 예외 처리 및 경로 설정
    ssl._create_default_https_context = ssl._create_unverified_context
    zip_path = os.path.join(base_dir, "kosdaq_code.zip")
    mst_path = os.path.join(base_dir, "kosdaq_code.mst")

    if verbose: print(f"Downloading master file to: {zip_path}")

    # 2. 마스터 파일 다운로드 및 압축 해제
    urllib.request.urlretrieve("https://new.real.download.dws.co.kr/common/master/kosdaq_code.mst.zip", zip_path)

    with zipfile.ZipFile(zip_path, 'r') as kosdaq_zip:
        kosdaq_zip.extractall(base_dir)

    if os.path.exists(zip_path):
        os.remove(zip_path)

    # 3. 임시 파일 생성 없이 메모리(StringIO)에서 데이터 정제
    part1_data = io.StringIO()
    part2_data = io.StringIO()

    if verbose: print("Parsing master file...")
    with open(mst_path, mode="r", encoding="cp949", errors='ignore') as f:
        for row in f:
            # 기존 한투의 바이트 쪼개기 로직 유지
            rf1 = row[0:len(row) - 222]
            rf1_1 = rf1[0:9].rstrip()
            rf1_2 = rf1[9:21].rstrip()
            rf1_3 = rf1[21:].strip()

            part1_data.write(f"{rf1_1},{rf1_2},{rf1_3}\n")

            rf2 = row[-222:]
            part2_data.write(rf2)

    # 포인터를 처음으로 되돌려 읽을 준비
    part1_data.seek(0)
    part2_data.seek(0)

    # 4. 데이터프레임 빌드
    part1_columns = ['단축코드', '표준코드', '한글종목명']
    df1 = pd.read_csv(part1_data, header=None, names=part1_columns, encoding='cp949')

    field_specs = [
        2, 1, 4, 4, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9,
        5, 5, 1, 1, 1, 2, 1, 1, 1, 2, 2, 2, 3, 1, 3, 12, 12, 8, 15, 21, 2, 7, 1, 1, 1,
        1, 9, 9, 9, 5, 9, 8, 9, 3, 1, 1, 1
    ]

    part2_columns = [
        '증권그룹구분코드', '시가총액 규모 구분 코드 유가', '지수업종 대분류 코드', '지수 업종 중분류 코드', '지수업종 소분류 코드',
        '벤처기업 여부 (Y/N)', '저유동성종목 여부', 'KRX 종목 여부', 'ETP 상품구분코드', 'KRX100 종목 여부 (Y/N)',
        'KRX 자동차 여부', 'KRX 반도체 여부', 'KRX 바이오 여부', 'KRX 은행 여부', '기업인수목적회사여부',
        'KRX 에너지 화학 여부', 'KRX 철강 여부', '단기과열종목구분코드', 'KRX 미디어 통신 여부', 'KRX 건설 여부',
        '(코스닥)투자주의환기종목여부', 'KRX 증권 구분', 'KRX 선박 구분', 'KRX섹터지수 보험여부', 'KRX섹터지수 운송여부',
        'KOSDAQ150지수여부 (Y,N)', '주식 기준가', '정규 시장 매매 수량 단위', '시간외 시장 매매 수량 단위', '거래정지 여부',
        '정리매매 여부', '관리 종목 여부', '시장 경고 구분 코드', '시장 경고위험 예고 여부', '불성실 공시 여부',
        '우회 상장 여부', '락구분 코드', '액면가 변경 구분 코드', '증자 구분 코드', '증거금 비율', '신용주문 가능 여부',
        '신용기간', '전일 거래량', '주식 액면가', '주식 상장 일자', '상장 주수(천)', '자본금', '결산 월',
        '공모 가격', '우선주 구분 코드', '공매도과열종목여부', '이상급등종목여부', 'KRX300 종목 여부 (Y/N)', '매출액',
        '영업이익', '경상이익', '단기순이익', 'ROE(자기자본이익률)', '기준년월', '전일기준 시가총액 (억)', '그룹사 코드',
        '회사신용한도초과여부', '담보대출가능여부', '대주가능여부'
    ]

    df2 = pd.read_fwf(part2_data, widths=field_specs, names=part2_columns)
    df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)

    # 5. 사용 후 깔끔하게 잔여 파일 삭제
    if os.path.exists(mst_path):
        os.remove(mst_path)

    if verbose: print("Done")
    return df


# 실행 예시
if __name__ == "__main__":
    df = get_kosdaq_master_dataframe(verbose=True)
    # 단축코드 맨 앞 'A' 문자 제거 및 정제하고 싶다면 여기서 추가 가공 가능
    df['단축코드'] = df['단축코드'].str.replace('A', '')
    df.to_excel('kosdaq_code.xlsx', index=False)