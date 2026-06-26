package com.blackrabbit.stock;

import java.util.List;

public interface StockService {

    /* 1. BlackRabbit 메인페이지 - WatchList (2026_0626에 추가) */
    List<StockDTO> getPresent_StockList();



}// StockService
