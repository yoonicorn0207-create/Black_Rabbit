package com.blackrabbit.stock;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Controller
public class StockController {


    @Autowired
    private StockService stockService;

    /* BlackRabbit 메인페이지 호출 */
    @RequestMapping("/stockMain")
    public String getStockMainPage() {
        return "stock_main";
    }//BlackRabbit 메인페이지 호출 (2026_0626에 추가)

    /* 1. BlackRabbit 메인페이지 - WatchList (2026_0626에 추가) */
    @RequestMapping(value = "/api/stockList", method = RequestMethod.GET)
    @ResponseBody
    public List<StockDTO> getPresent_stockList() {
        return stockService.getPresent_StockList();
    }//BlackRabbit 메인페이지 - WatchList 데이터 호출 [HC_stock_daily1 테이블] (2026_0626에 추가)


    /* 2. BlackRabbit 메인페이지 - 일별차트 (2026_0629) */
    @RequestMapping("/api/chartData")
    @ResponseBody
    public List<Map<String, Object>> getChartData(@RequestParam("code") String code, @RequestParam("period") String period) {
        // 1. Service를 통해 DB에서 데이터 조회
        List<StockDailyDTO> dailyList = stockService.getDailyStockChartData(code, period);


        // 2. ApexCharts가 인식할 수 있는 JSON 구조로 변환
        return dailyList.stream().map((StockDailyDTO sddto) -> {
            Map<String, Object> map = new HashMap<>();

            // 이제 여기서 sddto를 사용하면 됩니다.
            map.put("x", sddto.getStck_bsop_date());
            map.put("y", new double[]{
                    sddto.getStck_oprc(), // 시가
                    sddto.getStck_hgpr(), // 고가
                    sddto.getStck_lwpr(), // 저가
                    sddto.getStck_clpr()  // 종가
            });
            return map;
        }).collect(Collectors.toList());

    }//BlackRabbit 메인페이지 - 일별차트


    /* 3. BlackRabbit 메인페이지 - 분봉/시간봉 (2026_0630) */
    @RequestMapping("/api/minHourChartData")
    @ResponseBody
    public List<Map<String, Object>> getMinHourBar(@RequestParam("code") String code, @RequestParam("period") String period) {
        // 1. Service를 통해 DB에서 데이터 조회
        List<StockDailyDTO> dailyList = stockService.getMinHourChart(code, period);


        // 2. ApexCharts가 인식할 수 있는 JSON 구조로 변환
        return dailyList.stream().map((StockDailyDTO sddto) -> {
            Map<String, Object> map = new HashMap<>();

            // 이제 여기서 sddto를 사용하면 됩니다.
            map.put("x", sddto.getStck_bsop_date());
            map.put("y", new double[]{
                sddto.getStck_oprc(), // 시가
                sddto.getStck_hgpr(), // 고가
                sddto.getStck_lwpr(), // 저가
                sddto.getStck_clpr()  // 종가
            });
            return map;
        }).collect(Collectors.toList());

    }//BlackRabbit 메인페이지 - 분봉/시간봉


}// StockController
