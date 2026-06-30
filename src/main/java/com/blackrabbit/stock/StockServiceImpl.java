package com.blackrabbit.stock;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service("StockService")
public class StockServiceImpl implements StockService {

    @Autowired // Mapper 주입
    private StockMapper stockMapper;

    /* 1. BlackRabbit 메인페이지 - WatchList  (2026_0626에 추가) */
    @Override
    public List<StockDTO> getPresent_StockList() {

        List<StockDTO> stock_List = stockMapper.getPresent_StockList();

        return stock_List;
    }//BlackRabbit 메인페이지 - WatchList

    /* 2. BlackRabbit 메인페이지 - 일별차트 (2026_0629) */
    @Override
    public List<StockDailyDTO> getDailyStockChartData(String code, String period) {

        List<StockDailyDTO> stockDaily_chart = stockMapper.getDailyStockChartData(code, period);

        return stockDaily_chart;
    }//BlackRabbit 메인페이지 - 일별/주별/월별차트


    /* 3. BlackRabbit 메인페이지 - 분봉/ 시간봉 (2026_0630)*/
    @Override
    public List<StockDailyDTO> getMinHourChart(String code, String period) {
        List<StockDailyDTO> res = stockMapper.getMinHourChart(code, period);

        return res;
    }

    /* 4. BlackRabbit 메인페이지 - 회원 보유종목 리스트  (2026_0630) By.yoonicorn */
    @Override
    public List<UserHoldingStockDTO> getMyHoldings(String userId) {

        List<UserHoldingStockDTO> userHoldingStock = stockMapper.getUserHoldings(userId);

        return userHoldingStock;
    }// BlackRabbit 메인페이지 - 회원 보유종목 리스트




}// StockServiceImpl
