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


    /* 5. BlackRabbit 메인페이지 - 주식 매수 (2026_0701 추가) */
    //① 현재 주식의 현재가 조회 & 시용자의 현재 잔액 확인 및 차감
    int getCurrentPrice(@Param("stockCode") String stockCode);//현재 주식의 현재가 조회

    int getUserBalance(@Param("userId") String userId); //사용자의 현재 잔액 확인

    void updateUserBalance(@Param("userId") String userId, @Param("amount") int amount); // 사용자 예수금 잔액차감

    // ②. 보유 종목 추가 또는 수량 업데이트 (Upsert)
    boolean checkIfHolding(@Param("userId") String userId, @Param("stockCode") String stockCode); // 사용자 종목 보유 or 미보유 확인

    void updateHolding(@Param("userId") String userId,
                       @Param("stockCode") String stockCode,
                       @Param("quantity") int quantity,
                       @Param("currentPrice") int currentPrice);//보유 중이면 수량+평단 업데이트

    void insertHolding(@Param("userId") String userId,
                       @Param("stockCode") String stockCode,
                       @Param("stockName") String stockName,
                       @Param("quantity") int quantity,
                       @Param("currentPrice") int currentPrice);//없으면 신규 INSERT

    /* 6. BlackRabbit 메인페이지 - 주식 매도 (2026_0701 추가) */
    Integer getHoldingQuantity(@Param("userId") String userId, @Param("stockCode") String stockCode); //보유 종목 정보 조회 (보유 수량 확인용)

    void deleteHolding(@Param("userId") String userId, @Param("stockCode") String stockCode); // 전량 매도 시 테이블에서 데이터 삭제

    void reduceHolding(@Param("userId") String userId,
                       @Param("stockCode") String stockCode,
                       @Param("quantity") int quantity,
                       @Param("currentPrice") int currentPrice); //일부 매도 시 수량과 구매 금액 조정

    void addBalance(@Param("userId") String userId, @Param("amount") int amount);


}// StockMapper
