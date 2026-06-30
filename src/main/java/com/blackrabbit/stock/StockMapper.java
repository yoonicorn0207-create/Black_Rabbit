package com.blackrabbit.stock;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
@Mapper
public interface StockMapper {
    /* 1. BlackRabbit 메인페이지 - WatchList  (2026_0626에 추가) */
    List<StockDTO> getPresent_StockList();

    /* 2. BlackRabbit 메인페이지 - 일별차트 (2026_0629에 추가) */
    List<StockDailyDTO> getDailyStockChartData(@Param("code") String code, @Param("period") String period);

    /* 3. BlackRabbit 메인페이지 - 분봉/시간봉 (2026_0630에 추가) */
    List<StockDailyDTO> getMinHourChart(@Param("code") String code, @Param("period") String period);

    /* 4. BlackRabbit 메인페이지 - 회원 보유종목 리스트  (2026_0630) */
    List<UserHoldingStockDTO> getUserHoldings(String userId);

}// StockMapper
