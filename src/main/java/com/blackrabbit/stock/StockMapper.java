package com.blackrabbit.stock;

import org.apache.ibatis.annotations.Mapper;

import java.util.List;
@Mapper
public interface StockMapper {
    /* 1. BlackRabbit 메인페이지 - WatchList  (2026_0626에 추가) */
    List<StockDTO> getPresent_StockList();

    /* 2. BlackRabbit 메인페이지 - 일별차트 (2026_0629에 추가) */
    List<StockDailyDTO> getDailyStockChartData(String code);


}// StockMapper
