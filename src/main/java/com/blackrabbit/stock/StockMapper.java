package com.blackrabbit.stock;

import org.apache.ibatis.annotations.Mapper;

import java.util.List;
@Mapper
public interface StockMapper {
    /* 1. BlackRabbit 메인페이지 - WatchList  (2026_0626에 추가) */
    List<StockDTO> getPresent_StockList();

}// StockMapper
