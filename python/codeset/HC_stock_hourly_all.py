from datetime import datetime, date

from database import patchSingleRow

def createHourBarAllDaily(target_date):
    """
    종목 루프 없이 하루치 전체를 한 번에 처리
    종목 기준으로 for문 도는거랑 속도가 비교도 안됨..;;
    """
    try:
        sql = f"""
            INSERT INTO HC_stock_hourly (
                ticker, 
                stck_bsop_date, 
                stck_cntg_hour, 
                stck_oprc, 
                stck_hgpr, 
                stck_lwpr, 
                stck_prpr, 
                cntg_vol
            )
            SELECT 
                ticker, 
                stck_bsop_date, 
                CONCAT(SUBSTR(stck_cntg_hour, 1, 2), ':00:00'),
                SUBSTRING_INDEX(GROUP_CONCAT(stck_oprc ORDER BY stck_cntg_hour ASC), ',', 1),
                MAX(stck_hgpr),
                MIN(stck_lwpr),
                SUBSTRING_INDEX(GROUP_CONCAT(stck_prpr ORDER BY stck_cntg_hour DESC), ',', 1),
                SUM(cntg_vol)
            FROM HC_stock_minute2
            WHERE stck_bsop_date = '{target_date}'
            GROUP BY ticker, stck_bsop_date, SUBSTR(stck_cntg_hour, 1, 2);
        """
        patchSingleRow(sql, "시간봉 일괄 생성 실패")

    except Exception as e:
        print(f"{e}")



# 메인 실행부
if __name__ == "__main__":
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')

    print("하루치 데이터 일괄 생성 시작")
    createHourBarAllDaily(today_str)
    print("생성 종료")



