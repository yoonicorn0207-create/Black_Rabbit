package com.blackrabbit.stock;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.List;

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

}// StockController
