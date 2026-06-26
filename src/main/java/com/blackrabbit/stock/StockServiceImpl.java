package com.blackrabbit.stock;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

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





}// StockServiceImpl
