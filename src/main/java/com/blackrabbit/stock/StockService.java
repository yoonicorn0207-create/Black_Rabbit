package com.blackrabbit.stock;

import java.util.List;
import java.util.Map;

public interface StockService {

    /* 1. BlackRabbit 메인페이지 - WatchList (2026_0626에 추가) By.yoonicorn */
    List<StockDTO> getPresent_StockList();


    /* 2. BlackRabbit 메인페이지 - 일별차트 (2026_0629) By.yoonicorn */
    List<StockDailyDTO> getDailyStockChartData(String code, String period);

    /* 3. BlackRabbit 메인페이지 - 분봉/ 시간봉 (2026_0630) */
    List<StockDailyDTO> getMinHourChart(String code, String period);

    /* 4. BlackRabbit 메인페이지 - 회원 보유종목 리스트  (2026_0630) By.yoonicorn */
    List<UserHoldingStockDTO> getMyHoldings(String userId);




}// StockService
