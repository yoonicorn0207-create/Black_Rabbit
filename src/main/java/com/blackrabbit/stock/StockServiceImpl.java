package com.blackrabbit.stock;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

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


    /* 5. BlackRabbit 메인페이지 - 주식 매수 (2026_0701 추가) */
    @Override
    @Transactional // 매수 과정 전체를 하나의 트랜잭션으로 묶습니다.
    public boolean buyStock(String userId, String stockCode, String stockName, int quantity) {
        try {
            // 1. 현재 주식의 현재가 조회 (예: 358,500원)
            // stockMapper를 통해 현재가를 가져오는 메서드.
            int currentPrice = stockMapper.getCurrentPrice(stockCode);
            int totalAmount = currentPrice * quantity;

            // 2. 사용자의 현재 잔액 확인 및 차감
            int userBalance = stockMapper.getUserBalance(userId);
            if (userBalance < totalAmount) {
                return false; // 잔액 부족
            }
            stockMapper.updateUserBalance(userId, totalAmount); // 잔액 차감

            // 3. 보유 종목 추가 또는 수량 업데이트 (Upsert)
            // 보유 중이면 수량+평단 업데이트, 없으면 신규 INSERT
            boolean isHolding = stockMapper.checkIfHolding(userId, stockCode);
            if (isHolding) {
                stockMapper.updateHolding(userId, stockCode, quantity, currentPrice);
            } else {
                stockMapper.insertHolding(userId, stockCode, stockName, quantity, currentPrice);
            }

            return true;
        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("주문 처리 중 에러 발생, 트랜잭션 롤백");
        }
    }//BlackRabbit 메인페이지 - 주식 매수 (2026_0701 추가)

    /* 6. BlackRabbit 메인페이지 - 주식 매도 (2026_0701 추가) */
    @Override
    @Transactional // 매도 과정 전체를 트랜잭션으로 묶습니다.
    public boolean sellStock(String userId, String stockCode, int sellQuantity) {
        try {
            // 1. 보유 종목 정보 조회 (보유 수량 확인용)
            // UserHoldingStockDTO를 직접 가져오거나 mapper에서 수량을 확인합니다.
            Integer currentQuantity = stockMapper.getHoldingQuantity(userId, stockCode);

            // 2. 보유 종목이 없거나 수량이 부족하면 매도 불가
            if (currentQuantity == null || currentQuantity < sellQuantity) {
                return false;
            }

            // 3. 현재가 조회 (매도 금액 = 현재가 * 수량)
            int currentPrice = stockMapper.getCurrentPrice(stockCode);
            int totalSellAmount = currentPrice * sellQuantity;

            // 4. 보유 수량 업데이트 또는 행 삭제
            if (currentQuantity == sellQuantity) {
                // 전량 매도 시 테이블에서 데이터 삭제
                stockMapper.deleteHolding(userId, stockCode);
            } else {
                // 일부 매도 시 수량과 구매 금액 조정
                stockMapper.reduceHolding(userId, stockCode, sellQuantity, currentPrice);
            }

            // 5. 사용자의 잔액 증가 (매도 금액만큼)
            stockMapper.addBalance(userId, totalSellAmount);

            return true;
        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("매도 처리 중 에러 발생, 트랜잭션 롤백");
        }
    }//BlackRabbit 메인페이지 - 주식 매도 (2026_0701 추가)

}// StockServiceImpl
