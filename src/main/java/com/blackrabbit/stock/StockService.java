package com.blackrabbit.stock;

import java.util.List;
import java.util.Map;

public interface StockService {

    /* 1. BlackRabbit 메인페이지 - WatchList (2026_0626에 추가) */
    List<StockDTO> getPresent_StockList();


    /* 2. BlackRabbit 메인페이지 - 일별차트 (2026_0629) */
    List<StockDailyDTO> getDailyStockChartData(String code, String period);



}// StockService
